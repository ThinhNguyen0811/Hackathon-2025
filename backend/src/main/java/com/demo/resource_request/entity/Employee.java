package com.demo.resource_request.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Entity
@Table(name = "employees")
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class Employee {
    @Id
    private Integer id;
    private Integer userId;
    private String empCode;
    private String name;
    private String office;
    private String location;

    @OneToMany(mappedBy = "employee")
    private List<EmployeeSkill> employeeSkills;

    @OneToMany(mappedBy = "employee")
    private List<EmployeeAdditionalSkill> employeeAdditionalSkills;

    @OneToMany(mappedBy = "employee")
    private List<EmployeeBusinessDomain> employeeBusinessDomains;
}
