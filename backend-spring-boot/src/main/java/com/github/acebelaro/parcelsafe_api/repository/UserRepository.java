package com.github.acebelaro.parcelsafe_api.repository;

import com.github.acebelaro.parcelsafe_api.model.User;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends MongoRepository<User, String> {
    Optional<User> findByEmail(String email);
    Optional<User> findByUsername(String email);
    boolean existsByEmail(String email);
}