FROM eclipse-temurin:17-jdk AS builder

WORKDIR /app

# Copy the project source code
COPY . .

# Fix line endings and make the Maven wrapper executable
RUN chmod +x ./mvnw && \
    sed -i 's/\r$//' ./mvnw

# Build the application
RUN ./mvnw clean package -DskipTests

# Use a minimal base image for runtime
FROM eclipse-temurin:17-jre

WORKDIR /app

# Copy the built JAR from the builder stage
COPY --from=builder /app/target/*.jar app.jar

# Expose the application port
#EXPOSE 8081

# Run the Spring Boot application
ENTRYPOINT ["java", "-jar", "app.jar"]