package com.github.acebelaro.parcelsafe_api.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AuthResponse {
    private String token;
    private String message;
    private String userId;
    private String name;
    private String email;
}