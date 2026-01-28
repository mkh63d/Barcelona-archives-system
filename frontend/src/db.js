import Dexie from 'dexie'

// Initialize IndexedDB with Dexie
export const db = new Dexie('BarcelonaArchivesDB')

// Define database schema
db.version(1).stores({
  conversations: '++id, title, createdAt, updatedAt, messages',
})

// Conversation helper functions
export const conversationService = {
  // Create a new conversation
  async createConversation(title = 'New Conversation') {
    const conversation = {
      title,
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    const id = await db.conversations.add(conversation)
    return { id, ...conversation }
  },

  // Get all conversations (sorted by most recent)
  async getAllConversations() {
    return await db.conversations
      .orderBy('updatedAt')
      .reverse()
      .toArray()
  },

  // Get a specific conversation by ID
  async getConversation(id) {
    return await db.conversations.get(id)
  },

  // Update conversation messages
  async updateConversation(id, messages) {
    await db.conversations.update(id, {
      messages,
      updatedAt: new Date().toISOString(),
    })
  },

  // Update conversation title
  async updateTitle(id, title) {
    await db.conversations.update(id, {
      title,
      updatedAt: new Date().toISOString(),
    })
  },

  // Delete a conversation
  async deleteConversation(id) {
    await db.conversations.delete(id)
  },

  // Clear all conversations
  async clearAll() {
    await db.conversations.clear()
  },

  // Export conversation to JSON
  async exportConversation(id) {
    const conversation = await db.conversations.get(id)
    if (!conversation) return null
    
    const blob = new Blob([JSON.stringify(conversation, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `conversation-${conversation.title}-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  },

  // Import conversation from JSON
  async importConversation(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = async (e) => {
        try {
          const conversation = JSON.parse(e.target.result)
          delete conversation.id // Remove old ID
          conversation.createdAt = new Date().toISOString()
          conversation.updatedAt = new Date().toISOString()
          const id = await db.conversations.add(conversation)
          resolve({ id, ...conversation })
        } catch (error) {
          reject(error)
        }
      }
      reader.readAsText(file)
    })
  },

  // Search conversations by message content
  async searchConversations(query) {
    const allConversations = await db.conversations.toArray()
    return allConversations.filter(conv => 
      conv.title.toLowerCase().includes(query.toLowerCase()) ||
      conv.messages.some(msg => 
        msg.content.toLowerCase().includes(query.toLowerCase())
      )
    )
  },
}
