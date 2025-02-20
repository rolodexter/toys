# Use the official Dify images
FROM langgenius/dify-api:0.15.3 as api
FROM langgenius/dify-web:0.15.3 as web

# Final stage
FROM nginx:alpine

# Copy the Dify API files
COPY --from=api /app /app/api

# Copy the Dify web files
COPY --from=web /app /app/web

# Copy nginx configuration
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf

# Expose ports
EXPOSE 80

# Start services
CMD ["nginx", "-g", "daemon off;"]
