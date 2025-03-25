package com.demo.resource_request.mapper;

import com.demo.resource_request.dto.EmpInfoDto;
import com.demo.resource_request.entity.EmployeeBusinessDomain;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingConstants;
import org.mapstruct.ReportingPolicy;

import java.util.List;

@Mapper(
        unmappedTargetPolicy = ReportingPolicy.IGNORE,
        componentModel = MappingConstants.ComponentModel.SPRING
)
public interface EmployeeBusinessDomainMapper {

    @Mapping(target = "id", source = "id")
    @Mapping(target = "businessDomainId", source = "businessDomain.businessDomainId")
    @Mapping(target = "businessDomainName", source = "businessDomain.businessDomainName")
    @Mapping(target = "note", source = "note")
    EmpInfoDto.BusinessDomainDto toDto(EmployeeBusinessDomain entity);
    List<EmpInfoDto.BusinessDomainDto> toDtos(List<EmployeeBusinessDomain> entities);
}
