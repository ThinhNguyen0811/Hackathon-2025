package com.demo.resource_request.mapper;

import com.demo.resource_request.dto.EmpInfoDto;
import com.demo.resource_request.entity.EmployeeSkill;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingConstants;
import org.mapstruct.ReportingPolicy;

import java.util.List;

@Mapper(
        unmappedTargetPolicy = ReportingPolicy.IGNORE,
        componentModel = MappingConstants.ComponentModel.SPRING
)
public interface EmployeeSkillMapper {

    @Mapping(target = "id", source = "id")
    @Mapping(target = "skillId", source = "skill.skillId")
    @Mapping(target = "skillName", source = "skill.skillName")
    @Mapping(target = "proficiency", source = "proficiency.id")
    @Mapping(target = "proficiencyName", source = "proficiency.name")
    @Mapping(target = "monthOfExperience", defaultValue = "0", ignore = true)
    @Mapping(target = "primary", source = "primary")
    @Mapping(target = "note", source = "note")
    EmpInfoDto.SkillDto toDto(EmployeeSkill employeeSkill);

    List<EmpInfoDto.SkillDto> toDtos(List<EmployeeSkill> employeeSkills);
}
