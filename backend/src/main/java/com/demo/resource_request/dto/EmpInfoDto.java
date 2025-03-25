package com.demo.resource_request.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class EmpInfoDto {
    private List<EmployeeDto> employees;
    private Boolean isSyncing;
    private String lastSyncDate;

    @Data
    public static class EmployeeDto {
        private Integer id;
        private Integer userId;
        private String empCode;
        private String name;
        private String location;
        private String office;
        private List<SkillDto> skills;
        private List<AdditionalSkillDto> additionalSkills;
        private List<BusinessDomainDto> businessDomains;
    }

    @Data
    public static class SkillDto {
        private Integer id;
        private Integer skillId;
        private String skillName;
        private Integer proficiency;
        private String proficiencyName;
        private Integer monthOfExperience = 0;
        private boolean isPrimary;
        private String note;
    }

    @Data
    public static class AdditionalSkillDto {
        private Integer id;
        private Integer additionalSkillId;
        private String additionalSkillName;
        private Integer proficiency;
        private String proficiencyName;
        private String note;
    }

    @Data
    public static class BusinessDomainDto {
        private Integer id;
        private Integer businessDomainId;
        private String businessDomainName;
        private String note;
    }
}
