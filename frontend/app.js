class StudyPlannerApp {
    constructor() {
        this.apiUrl = window.location.origin;
        this.sessionId = null;
        this.isLoading = false;
        this.chatSessions = [];
        
        this.elements = {
            chatMessages: document.getElementById('chatMessages'),
            messageInput: document.getElementById('messageInput'),
            sendButton: document.getElementById('sendButton'),
            loadingOverlay: document.getElementById('loadingOverlay'),
            statusBadge: document.getElementById('statusBadge'),
            newChatBtn: document.getElementById('newChatBtn'),
            chatHistory: document.getElementById('chatHistory')
        };
        
        this.init();
    }
    
    async init() {
        this.setupEventListeners();
        await this.createSession();
        await this.loadChatHistory();
    }
    
    setupEventListeners() {
        this.elements.sendButton.addEventListener('click', () => this.sendMessage());
        this.elements.newChatBtn.addEventListener('click', () => this.newChat());
        
        this.elements.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }
    
    async checkHealth() {
        try {
            const response = await fetch(`${this.apiUrl}/api/health`);
            const data = await response.json();
            
            if (data.success) {
                this.updateConnectionStatus('Connected');
            } else {
                this.updateConnectionStatus('Error');
            }
        } catch (error) {
            console.error('Health check failed:', error);
            this.updateConnectionStatus('Disconnected');
        }
    }
    
    updateConnectionStatus(status) {
        if (this.elements.statusBadge) {
            this.elements.statusBadge.textContent = status;
        }
    }
    
    async createSession() {
        try {
            const response = await fetch(`${this.apiUrl}/api/session/new`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.sessionId = data.session_id;
            }
        } catch (error) {
            console.error('Failed to create session:', error);
        }
    }
    
    async loadChatHistory() {
        try {
            const response = await fetch(`${this.apiUrl}/api/sessions`);
            const data = await response.json();
            
            if (data.success && data.sessions) {
                this.renderChatHistory(data.sessions);
            }
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    }
    
    renderChatHistory(sessions) {
        // Filter to only show sessions with messages
        const sessionsWithMessages = sessions.filter(s => s.first_message && s.first_message.trim());
        
        if (sessionsWithMessages.length === 0) {
            this.elements.chatHistory.innerHTML = '<div class="history-empty">No chats yet</div>';
            return;
        }
        
        this.elements.chatHistory.innerHTML = '';
        
        sessionsWithMessages.forEach((session) => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            if (session.session_id === this.sessionId) {
                historyItem.classList.add('active');
            }
            
            const displayText = session.first_message.substring(0, 40) + 
                (session.first_message.length > 40 ? '...' : '');
            
            historyItem.textContent = displayText;
            historyItem.title = session.first_message;
            historyItem.addEventListener('click', () => this.loadChatSession(session.session_id));
            
            this.elements.chatHistory.appendChild(historyItem);
        });
    }
    
    async loadChatSession(sessionId) {
        this.sessionId = sessionId;
        
        try {
            const response = await fetch(`${this.apiUrl}/api/session/${sessionId}/history`);
            const data = await response.json();
            
            if (data.success && data.history) {
                this.displayChatMessages(data.history);
            }
        } catch (error) {
            console.error('Failed to load chat session:', error);
        }
        
        this.elements.messageInput.focus();
    }
    
    displayChatMessages(messages) {
        this.elements.chatMessages.innerHTML = '';
        
        messages.forEach(msg => {
            this.addMessage(msg.role, msg.content, {});
        });
    }
    
    async sendMessage() {
        const message = this.elements.messageInput.value.trim();
        
        if (!message || this.isLoading) {
            return;
        }
        
        this.addMessage('user', message);
        this.elements.messageInput.value = '';
        this.setLoading(true);
        
        // Show typing indicator as a message
        const typingMessageId = 'typing-' + Date.now();
        this.addTypingIndicator(typingMessageId);
        
        try {
            const response = await fetch(`${this.apiUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator(typingMessageId);
            
            if (data.success) {
                this.handleSuccessResponse(data);
            } else {
                this.addMessage('assistant', `Error: ${data.error || 'Something went wrong'}`);
            }
            
            await this.loadChatHistory();
        } catch (error) {
            console.error('Failed to send message:', error);
            this.removeTypingIndicator(typingMessageId);
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }
    
    handleSuccessResponse(data) {
        let responseText = data.response || 'I received your message.';
        
        this.addMessage('assistant', responseText, data);
        
        if (data.study_plan) {
            this.addStudyPlan(data.study_plan);
        }
        
        if (data.execution_result) {
            this.addCodeResult(data.execution_result);
        }
    }
    
    addMessage(role, content, metadata = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = this.formatMessageContent(content);
        
        messageDiv.appendChild(contentDiv);
        
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessageContent(content) {
        // Escape HTML
        let text = content
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        
        // Convert markdown-like formatting
        // Bold
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/__(.*?)__/g, '<strong>$1</strong>');
        
        // Italic
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        text = text.replace(/_(.*?)_/g, '<em>$1</em>');
        
        // Line breaks
        text = text.replace(/\n/g, '<br>');
        
        // Bullet points
        text = text.replace(/^\* (.*?)$/gm, '<li>$1</li>');
        text = text.replace(/(<li>.*?<\/li>)/s, '<ul>$1</ul>');
        text = text.replace(/<\/li>\n<li>/g, '</li><li>');
        
        // Numbered lists
        text = text.replace(/^\d+\. (.*?)$/gm, '<li>$1</li>');
        
        // Bold text with colon (like "Key:" or "Note:")
        text = text.replace(/([A-Z][a-z]+):/g, '<strong>$1:</strong>');
        
        return text;
    }
    
    addStudyPlan(plan) {
        const planDiv = document.createElement('div');
        planDiv.className = 'study-plan';
        
        let html = '<h4>📚 Your Study Plan</h4>';
        html += `<div class="study-plan-detail"><strong>Subject:</strong> ${this.escapeHtml(plan.subject)}</div>`;
        html += `<div class="study-plan-detail"><strong>Duration:</strong> ${this.escapeHtml(plan.duration_weeks)} weeks</div>`;
        html += `<div class="study-plan-detail"><strong>Hours/Week:</strong> ${this.escapeHtml(plan.hours_per_week)}</div>`;
        html += `<div class="study-plan-detail"><strong>Level:</strong> ${this.escapeHtml(plan.level)}</div>`;
        
        if (plan.milestones && plan.milestones.length > 0) {
            html += '<div class="study-plan-detail"><strong>Milestones:</strong><ul>';
            plan.milestones.forEach(m => {
                html += `<li>Week ${m.week}: ${this.escapeHtml(m.milestone)}</li>`;
            });
            html += '</ul></div>';
        }
        
        if (plan.quality_score) {
            html += `<div class="study-plan-detail"><strong>Quality Score:</strong> ${plan.quality_score}%</div>`;
        }
        
        planDiv.innerHTML = html;
        this.elements.chatMessages.appendChild(planDiv);
        this.scrollToBottom();
    }
    
    addCodeResult(result) {
        const codeDiv = document.createElement('div');
        codeDiv.className = 'study-plan';
        codeDiv.style.borderColor = result.success ? '#06B6D4' : '#EF4444';
        
        let html = '<h4>💻 Code Execution Result</h4>';
        
        if (result.output) {
            html += `<div class="study-plan-detail"><strong>Output:</strong><pre>${this.escapeHtml(result.output)}</pre></div>`;
        }
        
        if (result.error) {
            html += `<div class="study-plan-detail"><strong>Error:</strong><pre>${this.escapeHtml(result.error)}</pre></div>`;
        }
        
        codeDiv.innerHTML = html;
        this.elements.chatMessages.appendChild(codeDiv);
        this.scrollToBottom();
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    scrollToBottom() {
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        this.elements.sendButton.disabled = loading;
    }
    
    addTypingIndicator(typingMessageId) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';
        messageDiv.id = typingMessageId;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content typing-indicator';
        contentDiv.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        
        messageDiv.appendChild(contentDiv);
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    removeTypingIndicator(typingMessageId) {
        const typingElement = document.getElementById(typingMessageId);
        if (typingElement) {
            typingElement.remove();
        }
    }
    
    async newChat() {
        this.elements.messageInput.value = '';
        await this.createSession();
        
        this.elements.chatMessages.innerHTML = `
            <div class="welcome-message">
                <h2>👋 New Chat</h2>
                <p>Start a fresh conversation with your AI study assistant.</p>
                <p style="margin-top: 12px; font-size: 0.95rem; opacity: 0.9;">What would you like to learn?</p>
            </div>
        `;
        
        await this.loadChatHistory();
        this.elements.messageInput.focus();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new StudyPlannerApp();
});
