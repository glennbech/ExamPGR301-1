
FROM maven:3.8.6-eclipse-temurin-17 as build

WORKDIR /app

COPY . .

RUN mvn package -DskipTests

FROM eclipse-temurin:17-jre-alpine as runtime

WORKDIR /app

COPY --from=build /app/target/imagegenerator-0.0.1-SNAPSHOT.jar app.jar

ENV SQS_QUEUE_URL=""

ENTRYPOINT ["java", "-jar", "app.jar"]