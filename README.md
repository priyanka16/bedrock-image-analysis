# Image Analysis API with LangChain and AWS Bedrock

A modern, production-ready image analysis API that integrates AWS Bedrock Claude models with LangChain for advanced multimodal AI capabilities. Built with FastAPI for high performance and scalability.

## 🚀 Features

- **Latest Claude Models**: Uses Claude 3.5 Sonnet, Claude 3.5 Haiku, and Claude 3 Opus
- **Advanced LangChain Integration**: LangChain with multimodal support
- **Multiple Analysis Types**: Basic, structured, specialized, artistic, and technical analysis
- **Production Ready**: Comprehensive logging, error handling, and monitoring
- **RESTful API**: Clean FastAPI endpoints with automatic documentation
- **Flexible Architecture**: Modular design with routers and services
- **Request Tracking**: Unique request IDs for debugging and monitoring

## 📋 Requirements

- Python 3.8+
- AWS Account with Bedrock access
- AWS credentials configured
- Virtual environment (recommended)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/bedrock-image-analysis.git
cd bedrock-image-analysis
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure AWS Credentials
```bash
# Option 1: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1

# Option 2: AWS CLI
aws configure

# Option 3: Create .env file
cp .env.example .env
# Edit .env with your credentials
```

## 🚀 Quick Start

### Start the Server
```bash
python src/main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Health Check
```bash
curl http://localhost:8000/health
```

## 📚 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and endpoint list |
| GET | `/health` | Health check |
| GET | `/api/v1/health` | Service health check |
| GET | `/api/v1/prompts` | List available analysis types |

### Analysis Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analyze/basic` | Basic image analysis |
| POST | `/api/v1/analyze/structured` | Structured JSON analysis |
| POST | `/api/v1/analyze/specialized` | Specialized analysis with type parameter |


## 🔍 Analysis Types

### Available Analysis Types

- **`basic_analysis`** - General image description and analysis
- **`object_detection`** - Identify and count objects in the image
- **`text_recognition`** - Extract and transcribe visible text
- **`scene_analysis`** - Analyze setting, context, and environment
- **`advanced_analysis`** - Comprehensive multi-aspect analysis
- **`artistic_analysis`** - Artistic and aesthetic evaluation
- **`technical_analysis`** - Technical and photographic assessment

### Model Selection

The API automatically selects the best Claude model for each analysis type:

- **Claude 3.5 Haiku**: Fast, cost-effective for simple tasks
- **Claude 3.5 Sonnet**: Balanced performance for most analyses
- **Claude 3 Opus**: Highest capability for complex analyses

## 📝 Usage Examples

### Basic Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/analyze/basic" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/image.jpg"
```

### Structured Analysis (Returns JSON)
```bash
curl -X POST "http://localhost:8000/api/v1/analyze/structured" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/image.jpg"
```

### Specialized Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/analyze/specialized" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/image.jpg" \
  -F "analysis_type=object_detection"
```

### Python Example
```python
import requests

# Basic analysis
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/analyze/basic',
        files={'file': f}
    )
    result = response.json()
    print(result['result'])

# Specialized analysis
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/analyze/specialized',
        files={'file': f},
        data={'analysis_type': 'text_recognition'}
    )
    result = response.json()
    print(result['result'])
```

## 🏗️ Project Structure

```
├── src/
│   ├── main.py                    # Main application entry point
│   ├── config/
│   │   └── langchain_config.py    # LangChain and model configuration
│   ├── routers/
│   │   └── langchain_router.py    # API route handlers
│   ├── services/
│   │   └── image_analysis.py      # Core analysis logic
│   └── utils/
│       ├── image_utils.py         # Image processing utilities
│       └── logger_config.py       # Logging configuration
├── config/
│   └── logging_config.yaml        # Logging settings
├── data/
│   ├── images/                    # Sample images
│   └── temp/                      # Temporary file storage
├── logs/                          # Application logs
├── scripts/
│   └── monitor_logs.py            # Log monitoring script
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── postman_collection.json        # Postman API collection
```

## 📊 Response Format

### Successful Response
```json
{
  "success": true,
  "result": "Detailed analysis of the image...",
  "analysis_type": "basic",
  "metrics": {
    "total_time_seconds": 2.34,
    "inference_time_seconds": 1.89
  },
  "request_id": "req_1234",
  "processing_time": 2.45,
  "image": {
    "file_name": "image.jpg",
    "file_size_kb": 245.6,
    "mime_type": "image/jpeg"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "request_id": "req_1234",
  "processing_time": 0.12
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Required |
| `AWS_REGION` | AWS region | `us-east-1` |

### Model Configuration

Edit `src/config/langchain_config.py` to:
- Change model versions
- Adjust model parameters
- Modify analysis prompts
- Configure validation settings

## 📈 Monitoring and Logging

### Log Files
- Application logs: `logs/image_analysis.log`
- Structured JSON logging with request tracking
- Automatic log rotation

### Log Monitoring
```bash
# Monitor recent logs
python scripts/monitor_logs.py

# Generate performance report
python scripts/monitor_logs.py --metrics --json

# Check for errors
python scripts/monitor_logs.py --min-level error
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

### Manual Testing with Sample Images
```bash
# Test with provided sample images
curl -X POST "http://localhost:8000/api/v1/analyze/basic" \
  -F "file=@data/images/sample_image1.jpg"
```

## 🚀 Deployment

### Production Deployment
```bash
# Using Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app

# Using Docker (create Dockerfile)
docker build -t image-analysis-api .
docker run -p 8000:8000 image-analysis-api
```

### Environment Setup
- Configure AWS IAM roles for Bedrock access
- Set up proper logging directories
- Configure environment variables
- Set up monitoring and alerting

## 🔒 Security Considerations

- AWS credentials should never be committed to code
- Use IAM roles in production environments
- Implement rate limiting for production use
- Validate and sanitize uploaded images
- Monitor for unusual usage patterns

## 📄 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Postman Collection**: Import `postman_collection.json`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**AWS Credentials Error**
```bash
# Verify credentials
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

**Model Access Issues**
- Ensure Bedrock model access is enabled in AWS console
- Check regional availability of Claude models
- Verify IAM permissions for Bedrock

**Image Upload Issues**
- Maximum file size: 5MB
- Supported formats: JPG, PNG, GIF, BMP, WebP
- Check image dimensions (32x32 to 8192x8192 pixels)

### Getting Help

- Check the logs in `logs/image_analysis.log`
- Use the monitoring script: `python scripts/monitor_logs.py`
- Review the API documentation at `/docs`
- Check AWS Bedrock service status