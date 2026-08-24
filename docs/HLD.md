# \# High-Level Design (HLD)

# 

# \## AI Document Intelligence \& Question Answering System

# 

# \## 1. Purpose

# 

# This document describes the high-level design of the AI Document Intelligence \& Question Answering System.

# 

# The system allows users to upload PDF documents and ask natural-language questions about their content.

# 

# The application combines:

# 

# \- Document processing

# \- OCR

# \- Structure-aware chunking

# \- Embedding generation

# \- Vector search

# \- Conversational context

# \- Large language model generation

# \- Source attribution

# 

# \---

# 

# \# 2. System Overview

# 

# The system consists of the following major components:

# 

# ```text

# &#x20;                   +-------------------+

# &#x20;                   |      User         |

# &#x20;                   +---------+---------+

# &#x20;                             |

# &#x20;                             v

# &#x20;                   +-------------------+

# &#x20;                   | React Frontend    |

# &#x20;                   +---------+---------+

# &#x20;                             |

# &#x20;                        HTTP / API

# &#x20;                             |

# &#x20;                             v

# &#x20;                   +-------------------+

# &#x20;                   | FastAPI Backend   |

# &#x20;                   +---------+---------+

# &#x20;                             |

# &#x20;            +----------------+----------------+

# &#x20;            |                |                |

# &#x20;            v                v                v

# &#x20;     +-------------+  +-------------+  +-------------+

# &#x20;     | Document    |  | Retrieval   |  | Conversation|

# &#x20;     | Processing  |  | Services    |  | Services    |

# &#x20;     +------+------+  +------+------+  +-------------+

# &#x20;            |                |

# &#x20;            v                v

# &#x20;     +-------------+  +-------------+

# &#x20;     | Docling     |  | Embedding   |

# &#x20;     | + OCR       |  | + Vector    |

# &#x20;     +------+------+  | Retrieval   |

# &#x20;            |         +------+------+

# &#x20;            |                |

# &#x20;            +--------+-------+

# &#x20;                     |

# &#x20;                     v

# &#x20;             +---------------+

# &#x20;             | PostgreSQL    |

# &#x20;             | + pgvector    |

# &#x20;             +---------------+

# &#x20;                     |

# &#x20;                     v

# &#x20;             +---------------+

# &#x20;             | LLM / Ollama  |

# &#x20;             +---------------+

