package com.demo.resource_request.mapper;

import com.demo.resource_request.dto.EmpInfoDto;
import com.demo.resource_request.entity.EmployeeAdditionalSkill;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingConstants;
import org.mapstruct.ReportingPolicy;

import java.util.List;

@Mapper(
        unmappedTargetPolicy = ReportingPolicy.IGNORE,
        componentModel = MappingConstants.ComponentModel.SPRING
)
public interface EmployeeAdditionalSkillMapper {

    @Mapping(target = "id", source = "id")
    @Mapping(target = "additionalSkillId", source = "additionalSkill.additionalSkillId")
    @Mapping(target = "additionalSkillName", source = "additionalSkill.additionalSkillName")
    @Mapping(target = "proficiency", source = "proficiency.id")
    @Mapping(target = "proficiencyName", source = "proficiency.name")
    @Mapping(target = "note", source = "note")
    EmpInfoDto.AdditionalSkillDto toDto(EmployeeAdditionalSkill entity);
    List<EmpInfoDto.AdditionalSkillDto> toDtos(List<EmployeeAdditionalSkill> entities);
}
