package com.demo.resource_request.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "business_domains")
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class BusinessDomain {
    @Id
    private Integer id;
    private Integer businessDomainId;
    private String businessDomainName;
}
