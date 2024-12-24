# Local Setup for Prisma Migrations using MySQL

## Prerequisites

1. **Node.js**: Ensure you have Node.js installed. You can download it from [nodejs.org](https://nodejs.org/).
2. **Docker**: Ensure you have Docker installed. You can download it from [docker.com](https://www.docker.com/).

## Steps

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/RedKnightM/d2-stats-signature.git
    cd d2-stats-signature
    ```

2. **Install Dependencies**:
    ```sh
    npm install
    ```

3. **Set Up MySQL using Docker**:
    - Run the following command to start a MySQL container:
        ```sh
        docker run --name d2-stats-signature -e MYSQL_ROOT_PASSWORD=pass -e MYSQL_DATABASE=d2-stats-main -p 3306:33061 -d mysql:latest
        ```

4. **Set Up Environment Variables**:
    - Create a `.env` file in the root directory.
    - Add the following environment variable:
        ```env
        DATABASE_URL="mysql://root:pass@localhost:33061/d2-stats-main?schema=public"
        ```

5. **Run Prisma Migrations**:
    - Generate the Prisma client:
        ```sh
        npx prisma generate
        ```
    - Apply the migrations to your database:
        ```sh
        npx prisma migrate dev --name init
        ```

Your local setup for Prisma migrations using MySQL is now complete.