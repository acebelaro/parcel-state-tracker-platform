package com.github.acebelaro.parcelsafe_api.controller;

import com.github.acebelaro.parcelsafe_api.dto.AuthResponse;
import com.github.acebelaro.parcelsafe_api.dto.LoginRequest;
import com.github.acebelaro.parcelsafe_api.dto.RegistrationRequest;
import com.github.acebelaro.parcelsafe_api.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class AuthController {
    
    private final UserService userService;
    
    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@RequestBody RegistrationRequest request) {
        AuthResponse response = userService.register(request);
        return ResponseEntity.ok(response);
    }
    
    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@RequestBody LoginRequest request) {
        AuthResponse response = userService.login(request);
        return ResponseEntity.ok(response);
    }
}