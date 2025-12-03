FROM alpine:latest

WORKDIR /app

# Create the folders inside the container
RUN mkdir -p /app/data/chroma_db
RUN touch /app/data/news_intelligence.db

# Environment variables (optional defaults)
ENV CHROMA_DB_PATH=/app/data/chroma_db
ENV SQLITE_DB_PATH=/app/data/news_intelligence.db

# Print the paths when container runs
CMD echo "CHROMA_DB_PATH=$CHROMA_DB_PATH" && \
    echo "SQLITE_DB_PATH=$SQLITE_DB_PATH"
