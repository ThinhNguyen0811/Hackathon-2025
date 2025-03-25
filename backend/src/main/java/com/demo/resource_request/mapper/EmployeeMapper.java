package com.demo.resource_request.mapper;

import com.demo.resource_request.dto.EmpInfoDto;
import com.demo.resource_request.entity.Employee;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingConstants;
import org.mapstruct.ReportingPolicy;

import java.util.List;

@Mapper(
        unmappedTargetPolicy = ReportingPolicy.IGNORE,
        componentModel = MappingConstants.ComponentModel.SPRING,
        uses = {
                EmployeeSkillMapper.class,
                EmployeeAdditionalSkillMapper.class,
                EmployeeBusinessDomainMapper.class
        }
)
public interface EmployeeMapper {

    @Mapping(target = "skills", source = "employeeSkills")
    @Mapping(target = "additionalSkills", source = "employeeAdditionalSkills")
    @Mapping(target = "businessDomains", source = "employeeBusinessDomains")
    EmpInfoDto.EmployeeDto toDto(Employee entity);

    List<EmpInfoDto.EmployeeDto> toDtos(List<Employee> entities);
}
