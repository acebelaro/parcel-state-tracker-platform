package com.github.acebelaro.parcelsafe_api.service;

import com.github.acebelaro.parcelsafe_api.dto.AuthResponse;
import com.github.acebelaro.parcelsafe_api.dto.LoginRequest;
import com.github.acebelaro.parcelsafe_api.dto.RegistrationRequest;
import com.github.acebelaro.parcelsafe_api.model.User;
import com.github.acebelaro.parcelsafe_api.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    
    public AuthResponse register(RegistrationRequest request) {
        // Check if email already exists
        if (userRepository.existsByEmail(request.getEmail())) {
            return AuthResponse.builder()
                    .message("Email already exists")
                    .build();
        }
        
        // Create new user with encoded password
        User user = User.builder()
                .username(request.getUsername())
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .build();
        
        User savedUser = userRepository.save(user);
        
        return AuthResponse.builder()
                .message("User registered successfully")
                .userId(savedUser.getId())
                .name(savedUser.getUsername())
                .email(savedUser.getEmail())
                .build();
    }
    
    public AuthResponse login(LoginRequest request) {
        // Find user by email
        User user = userRepository.findByUsername(request.getUsername())
                .orElse(null);
        
        if (user == null) {
            return AuthResponse.builder()
                    .message("User not found")
                    .build();
        }
        
        // Check if password matches
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            return AuthResponse.builder()
                    .message("Invalid password")
                    .build();
        }
        
        return AuthResponse.builder()
                .message("Login successful")
                .userId(user.getId())
                .name(user.getUsername())
                .email(user.getEmail())
                .build();
    }
}