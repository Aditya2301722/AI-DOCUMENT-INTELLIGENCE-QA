import { useRef, useState } from "react"
import "./App.css"

import {
  sendChatMessage,
  uploadDocument,
  type ChatSource,
} from "./services/api"

type Message = {
  role: "user" | "assistant"
  content: string
  sources?: ChatSource[]
}

const SESSION_ID = 1

function App() {
  const [question, setQuestion] = useState("")
  const [messages, setMessages] = useState<Message[]>([])

  const [isLoading, setIsLoading] = useState(false)

  const [isUploading, setIsUploading] = useState(false)

  const [error, setError] = useState("")

  const [documentName, setDocumentName] = useState(
    "Return Policy",
  )

  const [documentStatus, setDocumentStatus] = useState(
    "Ready",
  )

  const [hasDocument, setHasDocument] = useState(true)

  const fileInputRef =
    useRef<HTMLInputElement | null>(null)

  // ============================================================
  // CHAT
  // ============================================================

  async function handleSend() {
    const message = question.trim()

    if (!message || isLoading || isUploading) {
      return
    }

    setError("")

    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: message,
      },
    ])

    setQuestion("")
    setIsLoading(true)

    try {
      const response = await sendChatMessage(
        SESSION_ID,
        message,
      )

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: response.answer,
          sources: response.sources,
        },
      ])
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Something went wrong."

      console.error(
        "Chat request failed:",
        error,
      )

      setError(errorMessage)

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            "I couldn't process your question. Please try again.",
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  // ============================================================
  // SUGGESTIONS
  // ============================================================

  function handleSuggestion(text: string) {
    setQuestion(text)
  }

  // ============================================================
  // UPLOAD BUTTON
  // ============================================================

  function handleUploadClick() {
    if (isUploading) {
      return
    }

    fileInputRef.current?.click()
  }

  // ============================================================
  // FILE SELECTION + UPLOAD
  // ============================================================

  async function handleFileSelected(
    event: React.ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0]

    // Reset input so selecting the same file again
    // will trigger onChange.
    event.target.value = ""

    if (!file) {
      return
    }

    // ----------------------------------------------------------
    // Validate PDF
    // ----------------------------------------------------------

    const isPdf =
      file.type === "application/pdf" ||
      file.name.toLowerCase().endsWith(".pdf")

    if (!isPdf) {
      setError("Please select a PDF file.")
      return
    }

    setError("")
    setIsUploading(true)
    setDocumentName(file.name)
    setDocumentStatus("Uploading...")
    setHasDocument(true)

    try {
      // --------------------------------------------------------
      // Send PDF to FastAPI
      // --------------------------------------------------------

      const response = await uploadDocument(file)

      console.log(
        "Document uploaded successfully:",
        response,
      )

      // --------------------------------------------------------
      // Update document state
      // --------------------------------------------------------

      setDocumentName(response.filename)
      setDocumentStatus("Ready")
      setHasDocument(true)

      // --------------------------------------------------------
      // Clear old conversation
      //
      // The knowledge base has changed, so old answers
      // should not remain visually mixed with the new PDF.
      // --------------------------------------------------------

      setMessages([])

      // --------------------------------------------------------
      // Show useful success information
      // --------------------------------------------------------

      setError(
        `Document ready: ${response.filename} (${response.chunk_count} chunks)`,
      )

      // Automatically remove the success message
      // after a few seconds.
      window.setTimeout(() => {
        setError("")
      }, 5000)
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Document upload failed."

      console.error(
        "Document upload failed:",
        error,
      )

      setError(errorMessage)

      // If upload failed, keep the current document
      // visible instead of pretending the new one is ready.
      setDocumentStatus(
        hasDocument ? "Ready" : "Upload failed",
      )
    } finally {
      setIsUploading(false)
    }
  }

  // ============================================================
  // SOURCE HELPERS
  // ============================================================

  function getSourceDocument(
    source: ChatSource,
  ) {
    if (typeof source.filename === "string") {
      return source.filename
    }

    if (typeof source.document_id === "string") {
      return source.document_id
    }

    return "Document"
  }

  function getSourcePages(
    source: ChatSource,
  ) {
    if (Array.isArray(source.page_numbers)) {
      return source.page_numbers.join(", ")
    }

    return "—"
  }

  function getSourceSection(
    source: ChatSource,
  ) {
    if (typeof source.section === "string") {
      return source.section
    }

    return "Relevant section"
  }

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="app-shell">

      {/* ====================================================== */}
      {/* SIDEBAR */}
      {/* ====================================================== */}

      <aside className="sidebar">

        {/* BRAND */}

        <div className="brand">

          <div className="brand-mark">
            ◈
          </div>

          <div className="brand-text">

            <strong>
              Knowledge
            </strong>

            <span>
              Assistant
            </span>

          </div>

        </div>

        {/* UPLOAD BUTTON */}

        <button
          className="upload-button"
          type="button"
          onClick={handleUploadClick}
          disabled={isUploading}
        >

          <span className="upload-icon">
            {isUploading ? "..." : "+"}
          </span>

          <span>
            {isUploading
              ? "Processing..."
              : "Upload PDF"}
          </span>

        </button>

        {/* HIDDEN FILE INPUT */}

        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf,.pdf"
          onChange={handleFileSelected}
          hidden
        />

        {/* DOCUMENTS */}

        <div className="sidebar-section">

          <div className="section-header">

            <span>
              DOCUMENTS
            </span>

            <span className="document-count">
              {hasDocument ? 1 : 0}
            </span>

          </div>

          <div className="document-list">

            {hasDocument && (

              <div className="document active">

                <div className="document-icon">
                  PDF
                </div>

                <div className="document-info">

                  <strong>
                    {documentName}
                  </strong>

                  <span>
                    {documentStatus}
                  </span>

                </div>

              </div>

            )}

          </div>

        </div>

        {/* ENGINE STATUS */}

        <div className="sidebar-bottom">

          <div className="engine-status">

            <span className="status-dot" />

            <div>

              <strong>
                RAG Engine
              </strong>

              <span>
                Connected
              </span>

            </div>

          </div>

        </div>

      </aside>

      {/* ====================================================== */}
      {/* MAIN CONTENT */}
      {/* ====================================================== */}

      <main className="main-content">

        {/* TOP BAR */}

        <header className="topbar">

          <div className="topbar-title">

            <span className="eyebrow">
              DOCUMENT INTELLIGENCE
            </span>

            <h2>
              Knowledge Workspace
            </h2>

          </div>

          <div className="system-status">

            <span className="status-dot" />

            <span>
              Online
            </span>

          </div>

        </header>

        {/* ==================================================== */}
        {/* CHAT */}
        {/* ==================================================== */}

        <section className="chat-area">

          {messages.length === 0 ? (

            <div className="empty-state">

              <div className="empty-icon">
                ◈
              </div>

              <span className="empty-eyebrow">
                YOUR KNOWLEDGE BASE
              </span>

              <h3>
                Ask your documents
              </h3>

              <p>
                Search your uploaded documents and
                get clear, grounded answers with
                relevant sources.
              </p>

              <div className="suggestion-grid">

                <button
                  type="button"
                  onClick={() =>
                    handleSuggestion(
                      "How long can damaged products be returned?",
                    )
                  }
                >

                  <span>
                    How long can damaged products
                    be returned?
                  </span>

                  <strong>
                    →
                  </strong>

                </button>

                <button
                  type="button"
                  onClick={() =>
                    handleSuggestion(
                      "What information is available in these documents?",
                    )
                  }
                >

                  <span>
                    What information is available
                    in these documents?
                  </span>

                  <strong>
                    →
                  </strong>

                </button>

              </div>

            </div>

          ) : (

            <div className="messages">

              {messages.map(
                (message, index) => (

                  <div
                    className={`message-row ${message.role}`}
                    key={index}
                  >

                    <div className="message-avatar">
                      {message.role === "user"
                        ? "You"
                        : "AI"}
                    </div>

                    <div className="message-content">

                      <span className="message-role">

                        {message.role === "user"
                          ? "You"
                          : "Knowledge Assistant"}

                      </span>

                      <p>
                        {message.content}
                      </p>

                      {/* SOURCES */}

                      {message.role ===
                        "assistant" &&
                        message.sources &&
                        message.sources.length >
                          0 && (

                          <div className="sources">

                            <div className="sources-header">

                              <div>

                                <span className="sources-title">
                                  SOURCES
                                </span>

                                <span className="sources-count">
                                  {
                                    message.sources
                                      .length
                                  }
                                </span>

                              </div>

                              <span className="sources-description">
                                Grounding evidence
                              </span>

                            </div>

                            <div className="source-list">

                              {message.sources.map(
                                (
                                  source,
                                  sourceIndex,
                                ) => (

                                  <div
                                    className="source-card"
                                    key={
                                      sourceIndex
                                    }
                                  >

                                    <div className="source-number">
                                      {
                                        sourceIndex +
                                        1
                                      }
                                    </div>

                                    <div className="source-icon">
                                      PDF
                                    </div>

                                    <div className="source-details">

                                      <strong>
                                        {getSourceDocument(
                                          source,
                                        )}
                                      </strong>

                                      <span>

                                        Page{" "}
                                        {getSourcePages(
                                          source,
                                        )}

                                        {" · "}

                                        {getSourceSection(
                                          source,
                                        )}

                                      </span>

                                    </div>

                                    <div className="source-arrow">
                                      →
                                    </div>

                                  </div>

                                ),
                              )}

                            </div>

                          </div>

                        )}

                    </div>

                  </div>

                ),
              )}

              {/* LOADING */}

              {isLoading && (

                <div className="message-row assistant">

                  <div className="message-avatar">
                    AI
                  </div>

                  <div className="message-content">

                    <span className="message-role">
                      Knowledge Assistant
                    </span>

                    <div className="typing">

                      <span />
                      <span />
                      <span />

                    </div>

                  </div>

                </div>

              )}

            </div>

          )}

        </section>

        {/* ERROR / STATUS */}

        {error && (

          <div className="error-message">
            {error}
          </div>

        )}

        {/* ==================================================== */}
        {/* COMPOSER */}
        {/* ==================================================== */}

        <section className="composer-wrapper">

          <div className="composer">

            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(
                  event.target.value,
                )
              }
              onKeyDown={(event) => {

                if (
                  event.key === "Enter" &&
                  !event.shiftKey
                ) {

                  event.preventDefault()

                  void handleSend()
                }

              }}
              placeholder="Ask anything about your documents..."
              rows={1}
              disabled={
                isLoading ||
                isUploading ||
                !hasDocument
              }
            />

            <button
              className="send-button"
              type="button"
              onClick={() =>
                void handleSend()
              }
              disabled={
                !question.trim() ||
                isLoading ||
                isUploading ||
                !hasDocument
              }
              aria-label="Send question"
            >

              {isLoading
                ? "..."
                : "↑"}

            </button>

          </div>

          <p className="composer-hint">
            Grounded answers from your uploaded
            documents
          </p>

        </section>

      </main>

    </div>
  )
}

export default App