package com.demo.resource_request.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Entity
@Table(name = "work_plans")
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class WorkPlan {
    @Id
    private Integer id;
    private Integer projectId;
    private Integer projectType;
    private Integer projectModel;
    private Integer employeeId;
    private String empCode;
    private LocalDate startDate;
    private LocalDate endDate;
    private Integer dailyHour;
    private String createdEmpCode;
}
