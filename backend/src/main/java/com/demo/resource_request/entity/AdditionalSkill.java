package com.demo.resource_request.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "additional_skills")
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class AdditionalSkill {
    @Id
    private Integer id;
    private Integer additionalSkillId;
    private String additionalSkillName;
}
