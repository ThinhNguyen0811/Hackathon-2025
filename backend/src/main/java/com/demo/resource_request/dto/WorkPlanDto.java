package com.demo.resource_request.dto;

import lombok.Builder;
import lombok.Data;

import java.time.Instant;
import java.util.List;

@Data
@Builder
public class WorkPlanDto {
    private Integer id;
    private Integer employeeId;
    private String empCode;
    private Integer projectId;
    private Integer projectModel;
    private Integer projectType;
    private Integer dailyHour;
    private Instant startDate;
    private Instant endDate;
    private List<String> skillNames;
    private String note;
    private String createdEmpCode;

}
