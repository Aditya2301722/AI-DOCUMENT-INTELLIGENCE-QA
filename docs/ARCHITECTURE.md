\# Deployment Architecture



\## AI Document Intelligence \& Question Answering System



This document describes the deployment architecture of the AI Document Intelligence \& Question Answering System.



The architecture is designed to separate the frontend, backend API, document processing pipeline, database, vector retrieval, and AI model services.



The current implementation runs locally. The deployment architecture described below represents the target architecture for deploying the application as a web-based service.



\---



\# 1. High-Level Architecture



```text

&#x20;                             INTERNET

&#x20;                                 |

&#x20;                                 v

&#x20;                       +-------------------+

&#x20;                       |   Web Browser     |

&#x20;                       |                   |

&#x20;                       | React Frontend    |

&#x20;                       +---------+---------+

&#x20;                                 |

&#x20;                                 | HTTPS

&#x20;                                 v

&#x20;                       +-------------------+

&#x20;                       |  Backend API      |

&#x20;                       |     FastAPI       |

&#x20;                       +---------+---------+

&#x20;                                 |

&#x20;             +-------------------+-------------------+

&#x20;             |                   |                   |

&#x20;             v                   v                   v

&#x20;     +---------------+   +---------------+   +---------------+

&#x20;     | PostgreSQL    |   | Document      |   | AI Services  |

&#x20;     | + pgvector    |   | Processing    |   |              |

&#x20;     |               |   | Pipeline      |   | Embeddings   |

&#x20;     | Sessions      |   |               |   | Generation   |

&#x20;     | Messages      |   | Docling       |   | Reranking    |

&#x20;     | Documents     |   | OCR           |   |              |

&#x20;     | Chunks        |   | Chunking      |   |              |

&#x20;     | Embeddings    |   | Embeddings    |   |              |

&#x20;     +---------------+   +---------------+   +---------------+

