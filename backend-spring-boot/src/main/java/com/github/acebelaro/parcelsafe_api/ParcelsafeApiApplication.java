package com.github.acebelaro.parcelsafe_api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.mongodb.config.EnableMongoAuditing;

@SpringBootApplication
@EnableMongoAuditing
public class ParcelsafeApiApplication {

	public static void main(String[] args) {
		SpringApplication.run(ParcelsafeApiApplication.class, args);
	}

}
