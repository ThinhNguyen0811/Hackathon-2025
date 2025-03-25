package com.demo.resource_request.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "employees_skills")
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class EmployeeSkill {
    @Id
    private Integer id;

    private boolean isPrimary;
    private String note;

    @ManyToOne
    @JoinColumn(name = "user_id")
    private Employee employee;

    @ManyToOne
    @JoinColumn(name = "skill_id")
    private Skill skill;

    @ManyToOne
    @JoinColumn(name = "proficiency_id")
    private Proficiency proficiency;
}
