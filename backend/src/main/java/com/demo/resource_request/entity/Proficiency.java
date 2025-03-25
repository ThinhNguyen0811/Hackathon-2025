package com.demo.resource_request.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "proficiencies")
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class Proficiency {
    @Id
    private Integer id;
    private String name;
}
