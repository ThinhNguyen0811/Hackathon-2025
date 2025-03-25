package com.demo.resource_request.dto;

import lombok.Builder;
import lombok.Data;

import java.time.Instant;
import java.util.List;

@Data
@Builder
public class LogTimeDto {
    private Integer skip;
    private Integer take;
    private String terms;
    private Integer total;
    private List<LogTimeDetailDto> result;

    @Data
    public static class LogTimeDetailDto {
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
        private Integer approvalOfficerId;
        private List<Integer> approvalOfficerIds;
        private String approveStatus;
        private Integer inquiryId;
        private Integer inquiryName;
        private Boolean isCanApproveOrReject;
        private Boolean isCanEdit;
        private Boolean isDelete;
    }
}
