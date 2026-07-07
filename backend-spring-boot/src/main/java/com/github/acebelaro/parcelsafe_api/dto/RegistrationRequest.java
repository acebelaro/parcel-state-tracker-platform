package com.github.acebelaro.parcelsafe_api.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class RegistrationRequest {
    private String name;
    private String email;
    private String password;
}