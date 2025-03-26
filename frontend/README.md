# Hackathon-2025 (Frontend) Environment Setup

This guide provides instructions for configuring environment variables on the frontend.

## Prerequisites
- Ensure you have [Node.js](https://nodejs.org/) installed (Recommended: LTS version)
- Install [Yarn](https://yarnpkg.com/) or use `npm`
- Clone the repository and navigate to the project folder

## Setup Environment Variables

1. Create a `.env.local` file in the root directory of your Next.js project.
2. Add the following environment variables:

```env
NEXT_PUBLIC_EMPINFO_API=""
NEXT_PUBLIC_INSIDER_API=""
NEXT_PUBLIC_TOKEN=""
NEXT_PUBLIC_AI_ENDPOINT=""
```
3. Replace the empty values ("") with the appropriate values.

## Install Dependencies
Run the following command to install the necessary dependencies:

```env
yarn install
# or
npm install
```

## Start Development Server

Run the development server with:
```env
yarn dev
# or
npm run dev
```

The application will be available at http://localhost:3000/ by default.

## Build and Run Production
To build and run the application in production mode:
```env
yarn build && yarn start
# or
npm run build && npm start
```

## Notes
- Environment variables prefixed with NEXT_PUBLIC_ are exposed to the browser. 
- Ensure sensitive information is not exposed through NEXT_PUBLIC_ variables.
