const API_BASE_URL = "http://127.0.0.1:8000"

export type ChatSource = {
  [key: string]: unknown
}

export type ChatResponse = {
  answer: string
  sources: ChatSource[]
}

export type UploadResponse = {
  status: string
  document_id: string
  filename: string
  session_id: number
  page_count: number
  chunk_count: number
  embedding_model: string
  replaced_document: string | null
}

export async function sendChatMessage(
  sessionId: number,
  message: string,
): Promise<ChatResponse> {
  const response = await fetch(
    `${API_BASE_URL}/chat/query`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: sessionId,
        message,
      }),
    },
  )

  if (!response.ok) {
    const errorText = await response.text()

    throw new Error(
      `Chat request failed (${response.status}): ${errorText}`,
    )
  }

  return response.json() as Promise<ChatResponse>
}

export async function uploadDocument(
  file: File,
): Promise<UploadResponse> {
  const formData = new FormData()

  formData.append("file", file)

  const response = await fetch(
    `${API_BASE_URL}/documents/upload`,
    {
      method: "POST",
      body: formData,
    },
  )

  if (!response.ok) {
    const errorText = await response.text()

    throw new Error(
      `Document upload failed (${response.status}): ${errorText}`,
    )
  }

  return response.json() as Promise<UploadResponse>
}