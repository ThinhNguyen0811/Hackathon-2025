package com.demo.resource_request.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "employees_additional_skills")
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class EmployeeAdditionalSkill {
    @Id
    private Integer id;

    private String note;

    @ManyToOne
    @JoinColumn(name = "user_id")
    private Employee employee;

    @ManyToOne
    @JoinColumn(name = "additional_skill_id")
    private AdditionalSkill additionalSkill;

    @ManyToOne
    @JoinColumn(name = "proficiency_id")
    private Proficiency proficiency;
}
