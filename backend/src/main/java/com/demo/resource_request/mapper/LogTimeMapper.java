package com.demo.resource_request.mapper;

import com.demo.resource_request.dto.LogTimeDto;
import com.demo.resource_request.entity.LogTime;
import org.mapstruct.Mapper;
import org.mapstruct.MappingConstants;
import org.mapstruct.ReportingPolicy;

import java.util.List;

@Mapper(
        unmappedTargetPolicy = ReportingPolicy.IGNORE,
        componentModel = MappingConstants.ComponentModel.SPRING
)
public interface LogTimeMapper {


    LogTimeDto.LogTimeDetailDto toDto(LogTime logTime);
    List<LogTimeDto.LogTimeDetailDto> toDtos(List<LogTime> logTimes);
}
