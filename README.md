# toys by rolodexter

<p align="center">
  <img src="images/GitHub_README_cover.png" alt="toys project cover" width="800">
</p>

<p align="center">
  A modern web application demonstrating Next.js, Flask, PostgreSQL, and Redis integration
</p>

<p align="center">
  <a href="https://github.com/rolodexter/toys">GitHub</a> ·
  <a href="https://toys.up.railway.app">Live Demo</a> ·
  <a href="docs/getting-started.md">Documentation</a>
</p>

## Overview

toys is a full-stack web application that showcases modern web development practices and cloud deployment strategies. Built with a Next.js frontend and Flask backend, it demonstrates seamless integration between various services and technologies.

### Key Features

- **Modern Stack**: Next.js frontend with Flask API backend
- **Database Integration**: PostgreSQL for persistent storage
- **Caching**: Redis for high-performance caching
- **Cloud Ready**: Optimized for Railway.app deployment
- **Developer Friendly**: Comprehensive logging and monitoring
- **Health Checks**: Built-in service health monitoring

## Architecture

The application is built with the following components:

- **Frontend**: Next.js application serving the user interface
- **Backend**: Flask API handling business logic and data operations
- **Database**: PostgreSQL for data persistence
- **Cache**: Redis for performance optimization
- **Deployment**: Railway.app for cloud hosting

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- Docker (optional)
- PostgreSQL
- Redis

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/rolodexter/toys.git
   cd toys
   ```

2. Install dependencies:
   ```bash
   # Frontend
   cd web
   npm install

   # Backend
   cd ../api
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Start the development servers:
   ```bash
   # Frontend
   cd web
   npm run dev

   # Backend
   cd ../api
   flask run
   ```

### Docker Deployment

```bash
docker-compose up -d
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Contributing Guidelines](docs/contributing.md)

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/contributing.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- GitHub: [@rolodexter](https://github.com/rolodexter)
- Email: [contact@rolodexter.com](mailto:contact@rolodexter.com)
