# K6 Performance Testing

K6 is a modern load testing tool that allows you to test the performance and reliability of your APIs. The tests in this directory are designed to validate the performance characteristics of the LangGraph API under various load conditions.

## Test Scenarios

### Available Tests

1. Burst - Kick off a burst of /run/wait requests.

## Running Tests Locally

### Prerequisites

1. Install k6: https://k6.io/docs/getting-started/installation/
2. Start your LangGraph API service
3. Ensure the API is accessible at `http://localhost:9123`

### Basic Usage

```bash
# Run burst test with default burst size (50)
make benchmark-burst

# Run burst test with custom burst size
BURST_SIZE=500 make benchmark-burst

# Run burst test against a deployment
BASE_URL=https://jdr-debug-31ac2c83eef557309f21c1e98d822025.us.langgraph.app make benchmark-burst

# Clean up result files
make benchmark-clean
```

### Output

Summary results are written to stdout and persisted in a summary_burst file. More detailed results for the same burst are persisted in a results_burst file.

## Resources

- [K6 Documentation](https://k6.io/docs/)
- [K6 JavaScript API](https://k6.io/docs/javascript-api/)
- [Performance Testing Best Practices](https://k6.io/docs/testing-guides/) 