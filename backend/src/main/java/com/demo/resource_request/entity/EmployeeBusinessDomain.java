package com.demo.resource_request.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "employees_business_domains")
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class EmployeeBusinessDomain {
    @Id
    private Integer id;

    private String note;

    @ManyToOne
    @JoinColumn(name = "user_id")
    private Employee employee;

    @ManyToOne
    @JoinColumn(name = "business_domain_id")
    private BusinessDomain businessDomain;
}
