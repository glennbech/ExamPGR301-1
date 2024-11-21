# Stage 1: Build stage
FROM maven:3.8.6-eclipse-temurin-17 as build

# Sett arbeidskatalog
WORKDIR /app

# Kopier prosjektfiler til containeren
COPY . .

# Bygg applikasjonen med Maven
RUN mvn package -DskipTests

# Stage 2: Runtime stage
FROM eclipse-temurin:17-jre-alpine as runtime

# Sett arbeidskatalog
WORKDIR /app

# Kopier den bygde JAR-filen fra byggstadiet
COPY --from=build /app/target/imagegenerator-0.0.1-SNAPSHOT.jar app.jar

# Definer miljøvariabelen for SQS URL
ENV SQS_QUEUE_URL=""

# Start applikasjonen
ENTRYPOINT ["java", "-jar", "app.jar"]