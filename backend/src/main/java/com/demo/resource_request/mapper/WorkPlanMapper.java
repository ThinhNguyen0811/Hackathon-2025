package com.demo.resource_request.mapper;

import com.demo.resource_request.dto.WorkPlanDto;
import com.demo.resource_request.entity.WorkPlan;
import org.mapstruct.*;

import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.List;

@Mapper(
        unmappedTargetPolicy = ReportingPolicy.IGNORE,
        componentModel = MappingConstants.ComponentModel.SPRING
)
public interface WorkPlanMapper {

    @Mapping(target = "skillNames", source = "workPlan", qualifiedByName = "mapToSkillName")
    @Mapping(target = "note", source = "workPlan", qualifiedByName = "mapToNote")
    @Mapping(target = "startDate", source = "startDate", qualifiedByName = "mapToInstant")
    @Mapping(target = "endDate", source = "endDate", qualifiedByName = "mapToInstant")
    WorkPlanDto toDto(WorkPlan workPlan);
    List<WorkPlanDto> toDtos(List<WorkPlan> workPlans);

    @Named("mapToSkillName")
    default List<String> mapToSkillName(WorkPlan workPlan) {
        return List.of("!net");
    }

    @Named("mapToNote")
    default String note(WorkPlan workPlan) {
        return "Lorem ipsum";
    }

    @Named("mapToInstant")
    default Instant mapToInstant(LocalDate localDate) {
        return localDate.atStartOfDay(ZoneId.systemDefault()).toInstant();
    }
}
