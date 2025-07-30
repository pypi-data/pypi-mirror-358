#!/bin/bash
# Test runner script for good-redis

set -e

echo "🧪 good-redis Test Runner"
echo "========================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || ! grep -q "good-redis" pyproject.toml; then
    echo -e "${RED}Error: Must run from libs/good-redis directory${NC}"
    exit 1
fi

# Function to check if Redis is available
check_redis() {
    if redis-cli -h localhost -p 6379 ping &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to check if Docker is available
check_docker() {
    if command -v docker &> /dev/null && docker ps &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Parse command line arguments
RUN_FAKEREDIS=true
RUN_REDIS=true
RUN_COVERAGE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --fakeredis-only)
            RUN_REDIS=false
            shift
            ;;
        --redis-only)
            RUN_FAKEREDIS=false
            shift
            ;;
        --coverage)
            RUN_COVERAGE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --fakeredis-only  Run only fakeredis tests"
            echo "  --redis-only      Run only real Redis tests"
            echo "  --coverage        Run with coverage report"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Install dependencies if needed
echo -e "${YELLOW}📦 Checking dependencies...${NC}"
uv sync

# Run fakeredis tests
if [ "$RUN_FAKEREDIS" = true ]; then
    echo -e "\n${YELLOW}🔧 Running fakeredis tests...${NC}"
    if uv run pytest -m "fakeredis" -v --tb=short; then
        echo -e "${GREEN}✅ Fakeredis tests passed${NC}"
    else
        echo -e "${RED}❌ Fakeredis tests failed${NC}"
        exit 1
    fi
fi

# Run Redis tests
if [ "$RUN_REDIS" = true ]; then
    echo -e "\n${YELLOW}🔧 Checking Redis availability...${NC}"
    
    if check_redis; then
        echo -e "${GREEN}✅ Local Redis available${NC}"
        echo -e "${YELLOW}🔧 Running Redis tests...${NC}"
        if uv run pytest -m "redis" -v --tb=short; then
            echo -e "${GREEN}✅ Redis tests passed${NC}"
        else
            echo -e "${RED}❌ Redis tests failed${NC}"
            exit 1
        fi
    elif check_docker; then
        echo -e "${YELLOW}🐳 Docker available, tests will use Docker Redis${NC}"
        echo -e "${YELLOW}🔧 Running Redis tests...${NC}"
        if uv run pytest -m "redis" -v --tb=short; then
            echo -e "${GREEN}✅ Redis tests passed${NC}"
        else
            echo -e "${RED}❌ Redis tests failed${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️  No Redis or Docker available, skipping Redis tests${NC}"
    fi
fi

# Run coverage if requested
if [ "$RUN_COVERAGE" = true ]; then
    echo -e "\n${YELLOW}📊 Running tests with coverage...${NC}"
    uv run pytest --cov=good_redis --cov-report=html --cov-report=term
    echo -e "${GREEN}✅ Coverage report generated in htmlcov/index.html${NC}"
fi

echo -e "\n${GREEN}🎉 All tests completed successfully!${NC}"