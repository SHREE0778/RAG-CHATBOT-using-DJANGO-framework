from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import DocumentUploadForm, UserRegistrationForm
from .models import Document, ChatMessage
from .services.embeddings import EmbeddingService
from .services.vector_store import VectorStoreService
from .services.llm_service import LLMService
from .services.document_processor import DocumentProcessor
import logging
# from chatbot.services.embeddings import EmbeddingService  <-- REMOVED

# embedding_service = EmbeddingService()  <-- MOVED TO LAZY LOADER
from chatbot.services.llm_service import LLMService

_llm_service = None
_embedding_service = None  # Lazy load singleton

def get_embedding_service():
    global _embedding_service
    if _embedding_service is None:
        # Import here to avoid loading torch at startup
        from chatbot.services.embeddings import EmbeddingService
        _embedding_service = EmbeddingService()
    return _embedding_service

def get_llm_service():
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


logger = logging.getLogger(__name__)


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to RAG Chatbot.')
            return redirect('chatbot:chat')
    else:
        form = UserRegistrationForm()
    return render(request, 'chatbot/register.html', {'form': form})

@login_required(login_url='chatbot:register')
def chat_view(request):
    """Main chat interface"""
    messages_list = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
    documents = Document.objects.filter(user=request.user, processed=True)
    
    context = {
        'messages': messages_list,
        'documents': documents,
        'has_documents': documents.exists()
    }
    return render(request, 'chatbot/chat.html', context)

@login_required
@require_http_methods(["POST"])
def send_message(request):
    """Handle chat message submission"""
    query = request.POST.get('message', '').strip()
    
    if not query:
        return JsonResponse({'error': 'Empty message'}, status=400)
    
    try:
        # Initialize vector store for user
        vector_store = VectorStoreService(request.user.id)
        
        # Generate query embedding
        query_embedding = get_embedding_service().generate_embedding(query)
        
        # Search for relevant documents
        search_results = vector_store.search(query_embedding, n_results=3)
        
        # Extract context from search results
        context = search_results.get('documents', [[]])[0] if search_results and search_results.get('documents') else []
        
        # Build chat history
        chat_history = []
        recent_messages = ChatMessage.objects.filter(
            user=request.user
        ).order_by('timestamp')[:5]
        
        for msg in recent_messages:
            chat_history.append({"role": "user", "content": msg.message})
            chat_history.append({"role": "assistant", "content": msg.response})
        
        # Generate response
        response = get_llm_service().generate_response(query, context, chat_history)
        
        # Save to database
        ChatMessage.objects.create(
            user=request.user,
            message=query,
            response=response
        )
        
        return JsonResponse({
            'response': response,
            'timestamp': 'Just now'
        })
    
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def upload_document(request):
    """Document upload and processing"""
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            
            # Create document record
            doc = Document.objects.create(
                user=request.user,
                filename=file.name,
                file=file,
                file_size=file.size
            )
            
            try:
                processor = DocumentProcessor()
                file_path = doc.file.path
                
                # Extract text based on file type
                if file.name.lower().endswith('.pdf'):
                    text = processor.extract_text_from_pdf(file_path)
                else:
                    text = processor.extract_text_from_txt(file_path)
                
                # Chunk text
                chunks = processor.chunk_text(text)
                
                # Generate embeddings
                embeddings = get_embedding_service().generate_embeddings(chunks)
                
                if not embeddings:
                    raise Exception("Failed to generate embeddings. Please check if HF_TOKEN is set in Render Environment Variables.")
                
                # Store in vector database
                vector_store = VectorStoreService(request.user.id)
                metadatas = [{'filename': file.name, 'doc_id': doc.id}] * len(chunks)
                vector_store.add_documents(chunks, embeddings, metadatas)
                
                # Mark as processed
                doc.processed = True
                doc.save()
                
                messages.success(
                    request, 
                    f'Document "{file.name}" uploaded and processed successfully! '
                    f'{len(chunks)} chunks created.'
                )
            
            except Exception as e:
                logger.error(f"Error processing document: {e}")
                messages.error(request, f'Error processing document: {str(e)}')
                doc.delete()
            
            return redirect('chatbot:upload')
    else:
        form = DocumentUploadForm()
    
    documents = Document.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'chatbot/upload.html', {
        'form': form,
        'documents': documents
    })

@login_required
@require_http_methods(["POST"])
def delete_document(request, doc_id):
    """Delete a document"""
    try:
        doc = Document.objects.get(id=doc_id, user=request.user)
        filename = doc.filename
        
        # Remove from vector store if method exists
        try:
            vector_store = VectorStoreService(request.user.id)
            if hasattr(vector_store, 'delete_by_metadata'):
                vector_store.delete_by_metadata({'doc_id': str(doc.id)})
        except Exception as e:
            logger.warning(f"Could not delete from vector store: {e}")
        
        doc.delete()
        messages.success(request, f'Document "{filename}" deleted successfully.')
    
    except Document.DoesNotExist:
        messages.error(request, 'Document not found.')
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        messages.error(request, 'Error deleting document. Please try again.')
    
    return redirect('chatbot:upload')

@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    return redirect('index')

@login_required
def clear_chat_history(request):
    """Clear user's chat history"""
    if request.method == 'POST':
        ChatMessage.objects.filter(user=request.user).delete()
        messages.success(request, 'Chat history cleared successfully.')
    return redirect('chatbot:chat')