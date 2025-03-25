package com.demo.resource_request.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Entity
@Table(name = "log_times")
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class LogTime {
    @Id
    private Integer id;
    private Integer userId;
    private String empCode;
    private String fullName;
    private Instant logDate;
    private Instant creationTime;
    private Instant lastModificationTime;
    private Integer projectId;
    private String projectName;
    private String pcName;
    private Integer hours;
    private Integer hourRate;
    private String activity;
    private String comment;
    private String loggedBy;
}
