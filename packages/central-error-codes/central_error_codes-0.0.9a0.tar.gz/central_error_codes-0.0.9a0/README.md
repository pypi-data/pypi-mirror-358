

```markdown
# Centralized Error Codes

## Overview
This repository provides a centralized collection of error codes that can be used across multiple microservices. It is designed to standardize error handling for both Node.js and Python-based applications.

## Publishing a New Node Module
Follow these steps to publish a new version of the module:

1. Install dependencies:
   ```sh
   npm i --save-dev @types/node
   ```
2. Build the project:
   ```sh
   npm run build
   ```
3. Package the module:
   ```sh
   npm pack
   ```
4. Publish the package to npm (ensure you are logged in):
   ```sh
   npm publish --access public
   ```
   If not logged in, run:
   ```sh
   npm login
   ```

## Installation
To use this package in a Node.js application, install it via npm:

```sh
npm install central-error-codes
```

## Usage in Node.js
Import and use the error codes in your application:

```typescript
import { ErrorCode } from "central-error-codes";

const ALL_ERROR_CODE = ErrorCode.getAllErrors();
const CMS_ERROR_CODE = ErrorCode.getCMSGatewayError();
```

## Usage in Python
For Python-based applications, usage instructions will be provided in a future update.

### Publishing a New Version for Python

To publish a new version of this package to PyPI, follow these steps:

1. Install the required tools:
   ```sh
   pip install setuptools wheel twine
   ```
2. Build the distribution files:
   ```sh
   python3 setup.py sdist bdist_wheel
   ```
   or alternatively:
   ```sh
   python3 -m build
   ```
3. Upload the package to PyPI using Twine:
   ```sh
   twine upload $(find dist -type f -not -path "dist/typescript/*")
   ```

