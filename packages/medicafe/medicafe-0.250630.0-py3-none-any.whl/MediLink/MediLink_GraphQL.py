# MediLink_GraphQL.py
"""
GraphQL module for United Healthcare Super Connector API
Handles query templates, query building, and response transformations
"""

import json
from typing import Dict, Any, Optional, List

class GraphQLQueryBuilder:
    """Builder class for constructing GraphQL queries for Super Connector API"""
    
    @staticmethod
    def get_eligibility_query() -> str:
        """
        Returns the GraphQL query for eligibility checks.
        Based on the Super Connector swagger documentation.
        """
        return """
        query CheckEligibility($input: EligibilityInput!) {
            checkEligibility(input: $input) {
                eligibility {
                    eligibilityInfo {
                        trnId
                        member {
                            memberId
                            firstName
                            lastName
                            middleName
                            suffix
                            dateOfBirth
                            gender
                            relationship
                            relationshipCode
                            relationshipTypeCode
                            individualRelationshipCode
                            dependentSequenceNumber
                        }
                        contact {
                            addresses {
                                type
                                street1
                                street2
                                city
                                state
                                country
                                zip
                                zip4
                            }
                        }
                        insuranceInfo {
                            policyNumber
                            eligibilityStartDate
                            eligibilityEndDate
                            planStartDate
                            planEndDate
                            policyStatus
                            planTypeDescription
                            planVariation
                            reportingCode
                            stateOfIssueCode
                            productType
                            productId
                            productCode
                            payerId
                            lineOfBusiness
                            lineOfBusinessCode
                            coverageTypes {
                                typeCode
                                description
                            }
                        }
                        associatedIds {
                            alternateId
                            medicaidRecipientId
                            exchangeMemberId
                            alternateSubscriberId
                            hicNumber
                            mbiNumber
                            subscriberMemberFacingIdentifier
                            survivingSpouseId
                            subscriberId
                            memberReplacementId
                            legacyMemberId
                            customerAccountIdentifier
                        }
                        planLevels {
                            level
                            family {
                                networkStatus
                                planAmount
                                planAmountFrequency
                                remainingAmount
                            }
                            individual {
                                networkStatus
                                planAmount
                                planAmountFrequency
                                remainingAmount
                            }
                        }
                        delegatedInfo {
                            entity
                            payerId
                            contact {
                                phone
                                fax
                                email
                            }
                            addresses {
                                type
                                street1
                                street2
                                city
                                state
                                country
                                zip
                                zip4
                            }
                        }
                        additionalInfo {
                            isReferralRequired
                        }
                    }
                    primaryCarePhysician {
                        isPcpFound
                        lastName
                        firstName
                        middleName
                        phoneNumber
                        address {
                            type
                            street1
                            street2
                            city
                            state
                            country
                            zip
                            zip4
                        }
                        networkStatusCode
                        affiliateHospitalName
                        providerGroupName
                    }
                    coordinationOfBenefit {
                        coordinationOfBenefitDetails {
                            payer {
                                id
                                name
                                phoneNumber
                                address {
                                    type
                                    street1
                                    street2
                                    city
                                    state
                                    country
                                    zip
                                    zip4
                                }
                            }
                            cobPrimacy {
                                indicator
                                description
                                message
                            }
                        }
                        uhgPrimacyStatus {
                            policyEffectiveDate
                            policyTerminationDate
                            primacy {
                                indicator
                                description
                                message
                            }
                        }
                    }
                    idCardImages {
                        side
                        content
                        contentType
                    }
                    providerNetwork {
                        status
                        tier
                    }
                    serviceLevels {
                        family {
                            networkStatus
                            services {
                                isVendorOnly
                                service
                                serviceCode
                                serviceDate
                                text
                                status
                                coPayAmount
                                coPayFrequency
                                coInsurancePercent
                                planAmount
                                remainingAmount
                                metYearToDateAmount
                                isReferralObtainedCopay
                                isReferralObtainedCoInsurance
                                referralCopayAmount
                                referralCoInsurancePercent
                                benefitsAllowedFrequencies
                                benefitsRemainingFrequencies
                                message {
                                    note {
                                        isSingleMessageDetail
                                        isViewDetail
                                        messages
                                        text
                                        subMessages {
                                            service
                                            status
                                            copay
                                            msg
                                            startDate
                                            endDate
                                            minCopay
                                            minCopayMsg
                                            maxCopay
                                            maxCopayMsg
                                            isPrimaryIndicator
                                        }
                                        limitationInfo {
                                            lmtPeriod
                                            lmtType
                                            lmtOccurPerPeriod
                                            lmtDollarPerPeriod
                                            message
                                        }
                                        isMultipleCopaysFound
                                        isMultipleCoinsuranceFound
                                    }
                                    coPay {
                                        isSingleMessageDetail
                                        isViewDetail
                                        messages
                                        text
                                        subMessages {
                                            service
                                            status
                                            copay
                                            msg
                                            startDate
                                            endDate
                                            minCopay
                                            minCopayMsg
                                            maxCopay
                                            maxCopayMsg
                                            isPrimaryIndicator
                                        }
                                        limitationInfo {
                                            lmtPeriod
                                            lmtType
                                            lmtOccurPerPeriod
                                            lmtDollarPerPeriod
                                            message
                                        }
                                        isMultipleCopaysFound
                                        isMultipleCoinsuranceFound
                                    }
                                    coInsurance {
                                        isSingleMessageDetail
                                        isViewDetail
                                        messages
                                        text
                                        subMessages {
                                            service
                                            status
                                            copay
                                            msg
                                            startDate
                                            endDate
                                            minCopay
                                            minCopayMsg
                                            maxCopay
                                            maxCopayMsg
                                            isPrimaryIndicator
                                        }
                                        limitationInfo {
                                            lmtPeriod
                                            lmtType
                                            lmtOccurPerPeriod
                                            lmtDollarPerPeriod
                                            message
                                        }
                                        isMultipleCopaysFound
                                        isMultipleCoinsuranceFound
                                    }
                                    deductible {
                                        isSingleMessageDetail
                                        isViewDetail
                                        messages
                                        text
                                        subMessages {
                                            service
                                            status
                                            copay
                                            msg
                                            startDate
                                            endDate
                                            minCopay
                                            minCopayMsg
                                            maxCopay
                                            maxCopayMsg
                                            isPrimaryIndicator
                                        }
                                        limitationInfo {
                                            lmtPeriod
                                            lmtType
                                            lmtOccurPerPeriod
                                            lmtDollarPerPeriod
                                            message
                                        }
                                        isMultipleCopaysFound
                                        isMultipleCoinsuranceFound
                                    }
                                    benefitsAllowed {
                                        isSingleMessageDetail
                                        isViewDetail
                                        messages
                                        text
                                        subMessages {
                                            service
                                            status
                                            copay
                                            msg
                                            startDate
                                            endDate
                                            minCopay
                                            minCopayMsg
                                            maxCopay
                                            maxCopayMsg
                                            isPrimaryIndicator
                                        }
                                        limitationInfo {
                                            lmtPeriod
                                            lmtType
                                            lmtOccurPerPeriod
                                            lmtDollarPerPeriod
                                            message
                                        }
                                        isMultipleCopaysFound
                                        isMultipleCoinsuranceFound
                                    }
                                    benefitsRemaining {
                                        isSingleMessageDetail
                                        isViewDetail
                                        messages
                                        text
                                        subMessages {
                                            service
                                            status
                                            copay
                                            msg
                                            startDate
                                            endDate
                                            minCopay
                                            minCopayMsg
                                            maxCopay
                                            maxCopayMsg
                                            isPrimaryIndicator
                                        }
                                        limitationInfo {
                                            lmtPeriod
                                            lmtType
                                            lmtOccurPerPeriod
                                            lmtDollarPerPeriod
                                            message
                                        }
                                        isMultipleCopaysFound
                                        isMultipleCoinsuranceFound
                                    }
                                    coPayList
                                    coInsuranceList
                                }
                            }
                        }
                        individual {
                            networkStatus
                            services {
                                isVendorOnly
                                service
                                serviceCode
                                serviceDate
                                text
                                status
                                coPayAmount
                                coPayFrequency
                                coInsurancePercent
                                planAmount
                                remainingAmount
                                metYearToDateAmount
                                isReferralObtainedCopay
                                isReferralObtainedCoInsurance
                                referralCopayAmount
                                referralCoInsurancePercent
                                benefitsAllowedFrequencies
                                benefitsRemainingFrequencies
                                message {
                                    note {
                                        isSingleMessageDetail
                                        isViewDetail
                                        messages
                                        text
                                        subMessages {
                                            service
                                            status
                                            copay
                                            msg
                                            startDate
                                            endDate
                                            minCopay
                                            minCopayMsg
                                            maxCopay
                                            maxCopayMsg
                                            isPrimaryIndicator
                                        }
                                        limitationInfo {
                                            lmtPeriod
                                            lmtType
                                            lmtOccurPerPeriod
                                            lmtDollarPerPeriod
                                            message
                                        }
                                        isMultipleCopaysFound
                                        isMultipleCoinsuranceFound
                                    }
                                    coPay {
                                        isSingleMessageDetail
                                        isViewDetail
                                        messages
                                        text
                                        subMessages {
                                            service
                                            status
                                            copay
                                            msg
                                            startDate
                                            endDate
                                            minCopay
                                            minCopayMsg
                                            maxCopay
                                            maxCopayMsg
                                            isPrimaryIndicator
                                        }
                                        limitationInfo {
                                            lmtPeriod
                                            lmtType
                                            lmtOccurPerPeriod
                                            lmtDollarPerPeriod
                                            message
                                        }
                                        isMultipleCopaysFound
                                        isMultipleCoinsuranceFound
                                    }
                                    coInsurance {
                                        isSingleMessageDetail
                                        isViewDetail
                                        messages
                                        text
                                        subMessages {
                                            service
                                            status
                                            copay
                                            msg
                                            startDate
                                            endDate
                                            minCopay
                                            minCopayMsg
                                            maxCopay
                                            maxCopayMsg
                                            isPrimaryIndicator
                                        }
                                        limitationInfo {
                                            lmtPeriod
                                            lmtType
                                            lmtOccurPerPeriod
                                            lmtDollarPerPeriod
                                            message
                                        }
                                        isMultipleCopaysFound
                                        isMultipleCoinsuranceFound
                                    }
                                    deductible {
                                        isSingleMessageDetail
                                        isViewDetail
                                        messages
                                        text
                                        subMessages {
                                            service
                                            status
                                            copay
                                            msg
                                            startDate
                                            endDate
                                            minCopay
                                            minCopayMsg
                                            maxCopay
                                            maxCopayMsg
                                            isPrimaryIndicator
                                        }
                                        limitationInfo {
                                            lmtPeriod
                                            lmtType
                                            lmtOccurPerPeriod
                                            lmtDollarPerPeriod
                                            message
                                        }
                                        isMultipleCopaysFound
                                        isMultipleCoinsuranceFound
                                    }
                                    benefitsAllowed {
                                        isSingleMessageDetail
                                        isViewDetail
                                        messages
                                        text
                                        subMessages {
                                            service
                                            status
                                            copay
                                            msg
                                            startDate
                                            endDate
                                            minCopay
                                            minCopayMsg
                                            maxCopay
                                            maxCopayMsg
                                            isPrimaryIndicator
                                        }
                                        limitationInfo {
                                            lmtPeriod
                                            lmtType
                                            lmtOccurPerPeriod
                                            lmtDollarPerPeriod
                                            message
                                        }
                                        isMultipleCopaysFound
                                        isMultipleCoinsuranceFound
                                    }
                                    benefitsRemaining {
                                        isSingleMessageDetail
                                        isViewDetail
                                        messages
                                        text
                                        subMessages {
                                            service
                                            status
                                            copay
                                            msg
                                            startDate
                                            endDate
                                            minCopay
                                            minCopayMsg
                                            maxCopay
                                            maxCopayMsg
                                            isPrimaryIndicator
                                        }
                                        limitationInfo {
                                            lmtPeriod
                                            lmtType
                                            lmtOccurPerPeriod
                                            lmtDollarPerPeriod
                                            message
                                        }
                                        isMultipleCopaysFound
                                        isMultipleCoinsuranceFound
                                    }
                                    coPayList
                                    coInsuranceList
                                }
                            }
                        }
                    }
                    extendedAttributes {
                        fundingCode
                        fundingType
                        hsa
                        cdhp
                        governmentProgramCode
                        cmsPackageBenefitPlanCode
                        cmsSegmentId
                        cmsContractId
                        marketType
                        obligorId
                        marketSite
                        benefitPlanId
                        virtualVisit
                        planVariation
                        groupNumber
                        legacyPanelNumber
                        coverageLevel
                        sharedArrangement
                        productServiceCode
                        designatedVirtualClinicNetwork
                        medicaidVariableCode
                        healthInsuranceExchangeId
                        memberDiv
                        legalEntityCode
                    }
                    otherBeneficiaries {
                        memberId
                        firstName
                        lastName
                        middleName
                        suffix
                        dateOfBirth
                        gender
                        relationship
                        relationshipCode
                        relationshipTypeCode
                        individualRelationshipCode
                        dependentSequenceNumber
                    }
                }
            }
        }
        """
    
    @staticmethod
    def build_eligibility_variables(
        member_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        service_start_date: Optional[str] = None,
        service_end_date: Optional[str] = None,
        coverage_types: Optional[List[str]] = None,
        payer_id: Optional[str] = None,
        provider_last_name: Optional[str] = None,
        provider_first_name: Optional[str] = None,
        provider_npi: Optional[str] = None,
        group_number: Optional[str] = None,
        trn_id: Optional[str] = None,
        service_level_codes: Optional[List[str]] = None,
        plan_start_date: Optional[str] = None,
        plan_end_date: Optional[str] = None,
        family_indicator: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Builds the variables object for the eligibility GraphQL query.
        
        Args:
            member_id: Unique identifier for the member
            first_name: First name of the member
            last_name: Last name of the member
            date_of_birth: Date of birth in ISO 8601 format (YYYY-MM-DD)
            service_start_date: Start date of the service in ISO 8601 format
            service_end_date: End date of the service in ISO 8601 format
            coverage_types: Types of coverage to include (e.g., ["Medical", "Behavioral"])
            payer_id: Payer identifier
            provider_last_name: Last name of the provider
            provider_first_name: First name of the provider
            provider_npi: National Provider Identifier (NPI) of the provider
            group_number: Group number
            trn_id: Transaction identifier
            service_level_codes: Service level codes (max 10)
            plan_start_date: Start date of the plan in ISO 8601 format
            plan_end_date: End date of the plan in ISO 8601 format
            family_indicator: Indicator for family/individual
            
        Returns:
            Dictionary containing the variables for the GraphQL query
        """
        variables = {
            "memberId": member_id
        }
        
        # Add optional parameters if provided
        if first_name:
            variables["firstName"] = first_name
        if last_name:
            variables["lastName"] = last_name
        if date_of_birth:
            variables["dateOfBirth"] = date_of_birth
        if service_start_date:
            variables["serviceStartDate"] = service_start_date
        if service_end_date:
            variables["serviceEndDate"] = service_end_date
        if coverage_types:
            variables["coverageTypes"] = coverage_types
        if payer_id:
            variables["payerId"] = payer_id
        if provider_last_name:
            variables["providerLastName"] = provider_last_name
        if provider_first_name:
            variables["providerFirstName"] = provider_first_name
        if provider_npi:
            variables["providerNPI"] = provider_npi
        if group_number:
            variables["groupNumber"] = group_number
        if trn_id:
            variables["trnId"] = trn_id
        if service_level_codes:
            variables["serviceLevelCodes"] = service_level_codes
        if plan_start_date:
            variables["planStartDate"] = plan_start_date
        if plan_end_date:
            variables["planEndDate"] = plan_end_date
        if family_indicator:
            variables["familyIndicator"] = family_indicator
            
        return variables
    
    @staticmethod
    def build_eligibility_request(variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds the complete GraphQL request body for eligibility checks.
        
        Args:
            variables: Variables dictionary for the GraphQL query
            
        Returns:
            Complete GraphQL request body
        """
        return {
            "query": GraphQLQueryBuilder.get_eligibility_query(),
            "variables": {
                "input": variables
            }
        }

    @staticmethod
    def get_sample_eligibility_request() -> Dict[str, Any]:
        """
        Returns the sample GraphQL request from the swagger documentation.
        This is for testing purposes to verify the endpoint is working.
        """
        return {
            "query": "query CheckEligibility($input: EligibilityInput!) { checkEligibility(input: $input) { eligibility { eligibilityInfo { trnId member { memberId firstName lastName middleName suffix dateOfBirth gender relationship relationshipCode relationshipTypeCode individualRelationshipCode dependentSequenceNumber } contact { addresses { type street1 street2 city state country zip zip4 } } insuranceInfo { policyNumber eligibilityStartDate eligibilityEndDate planStartDate planEndDate policyStatus planTypeDescription planVariation reportingCode stateOfIssueCode productType productId productCode payerId lineOfBusiness lineOfBusinessCode coverageTypes { typeCode description } } associatedIds { alternateId medicaidRecipientId exchangeMemberId alternateSubscriberId hicNumber mbiNumber subscriberMemberFacingIdentifier survivingSpouseId subscriberId memberReplacementId legacyMemberId customerAccountIdentifier } planLevels { level family { networkStatus planAmount planAmountFrequency remainingAmount } individual { networkStatus planAmount planAmountFrequency remainingAmount } } delegatedInfo { entity payerId contact { phone fax email } addresses { type street1 street2 city state country zip zip4 } } additionalInfo { isReferralRequired } } primaryCarePhysician { isPcpFound lastName firstName middleName phoneNumber address { type street1 street2 city state country zip zip4 } networkStatusCode affiliateHospitalName providerGroupName } coordinationOfBenefit { coordinationOfBenefitDetails { payer { id name phoneNumber address { type street1 street2 city state country zip zip4 } } cobPrimacy { indicator description message } } uhgPrimacyStatus { policyEffectiveDate policyTerminationDate primacy { indicator description message } } } idCardImages { side content contentType } providerNetwork { status tier } serviceLevels { family { networkStatus services { isVendorOnly service serviceCode serviceDate text status coPayAmount coPayFrequency coInsurancePercent planAmount remainingAmount metYearToDateAmount isReferralObtainedCopay isReferralObtainedCoInsurance referralCopayAmount referralCoInsurancePercent benefitsAllowedFrequencies benefitsRemainingFrequencies message { note { isSingleMessageDetail isViewDetail messages text subMessages { service status copay msg startDate endDate minCopay minCopayMsg maxCopay maxCopayMsg isPrimaryIndicator } limitationInfo { lmtPeriod lmtType lmtOccurPerPeriod lmtDollarPerPeriod message } isMultipleCopaysFound isMultipleCoinsuranceFound } coPay { isSingleMessageDetail isViewDetail messages text subMessages { service status copay msg startDate endDate minCopay minCopayMsg maxCopay maxCopayMsg isPrimaryIndicator } limitationInfo { lmtPeriod lmtType lmtOccurPerPeriod lmtDollarPerPeriod message } isMultipleCopaysFound isMultipleCoinsuranceFound } coInsurance { isSingleMessageDetail isViewDetail messages text subMessages { service status copay msg startDate endDate minCopay minCopayMsg maxCopay maxCopayMsg isPrimaryIndicator } limitationInfo { lmtPeriod lmtType lmtOccurPerPeriod lmtDollarPerPeriod message } isMultipleCopaysFound isMultipleCoinsuranceFound } deductible { isSingleMessageDetail isViewDetail messages text subMessages { service status copay msg startDate endDate minCopay minCopayMsg maxCopay maxCopayMsg isPrimaryIndicator } limitationInfo { lmtPeriod lmtType lmtOccurPerPeriod lmtDollarPerPeriod message } isMultipleCopaysFound isMultipleCoinsuranceFound } benefitsAllowed { isSingleMessageDetail isViewDetail messages text subMessages { service status copay msg startDate endDate minCopay minCopayMsg maxCopay maxCopayMsg isPrimaryIndicator } limitationInfo { lmtPeriod lmtType lmtOccurPerPeriod lmtDollarPerPeriod message } isMultipleCopaysFound isMultipleCoinsuranceFound } benefitsRemaining { isSingleMessageDetail isViewDetail messages text subMessages { service status copay msg startDate endDate minCopay minCopayMsg maxCopay maxCopayMsg isPrimaryIndicator } limitationInfo { lmtPeriod lmtType lmtOccurPerPeriod lmtDollarPerPeriod message } isMultipleCopaysFound isMultipleCoinsuranceFound } coPayList coInsuranceList } } } individual { networkStatus services { isVendorOnly service serviceCode serviceDate text status coPayAmount coPayFrequency coInsurancePercent planAmount remainingAmount metYearToDateAmount isReferralObtainedCopay isReferralObtainedCoInsurance referralCopayAmount referralCoInsurancePercent benefitsAllowedFrequencies benefitsRemainingFrequencies message { note { isSingleMessageDetail isViewDetail messages text subMessages { service status copay msg startDate endDate minCopay minCopayMsg maxCopay maxCopayMsg isPrimaryIndicator } limitationInfo { lmtPeriod lmtType lmtOccurPerPeriod lmtDollarPerPeriod message } isMultipleCopaysFound isMultipleCoinsuranceFound } coPay { isSingleMessageDetail isViewDetail messages text subMessages { service status copay msg startDate endDate minCopay minCopayMsg maxCopay maxCopayMsg isPrimaryIndicator } limitationInfo { lmtPeriod lmtType lmtOccurPerPeriod lmtDollarPerPeriod message } isMultipleCopaysFound isMultipleCoinsuranceFound } coInsurance { isSingleMessageDetail isViewDetail messages text subMessages { service status copay msg startDate endDate minCopay minCopayMsg maxCopay maxCopayMsg isPrimaryIndicator } limitationInfo { lmtPeriod lmtType lmtOccurPerPeriod lmtDollarPerPeriod message } isMultipleCopaysFound isMultipleCoinsuranceFound } deductible { isSingleMessageDetail isViewDetail messages text subMessages { service status copay msg startDate endDate minCopay minCopayMsg maxCopay maxCopayMsg isPrimaryIndicator } limitationInfo { lmtPeriod lmtType lmtOccurPerPeriod lmtDollarPerPeriod message } isMultipleCopaysFound isMultipleCoinsuranceFound } benefitsAllowed { isSingleMessageDetail isViewDetail messages text subMessages { service status copay msg startDate endDate minCopay minCopayMsg maxCopay maxCopayMsg isPrimaryIndicator } limitationInfo { lmtPeriod lmtType lmtOccurPerPeriod lmtDollarPerPeriod message } isMultipleCopaysFound isMultipleCoinsuranceFound } benefitsRemaining { isSingleMessageDetail isViewDetail messages text subMessages { service status copay msg startDate endDate minCopay minCopayMsg maxCopay maxCopayMsg isPrimaryIndicator } limitationInfo { lmtPeriod lmtType lmtOccurPerPeriod lmtDollarPerPeriod message } isMultipleCopaysFound isMultipleCoinsuranceFound } coPayList coInsuranceList } } } } extendedAttributes { fundingCode fundingType hsa cdhp governmentProgramCode cmsPackageBenefitPlanCode cmsSegmentId cmsContractId marketType obligorId marketSite benefitPlanId virtualVisit planVariation groupNumber legacyPanelNumber coverageLevel sharedArrangement productServiceCode designatedVirtualClinicNetwork medicaidVariableCode healthInsuranceExchangeId memberDiv legalEntityCode } otherBeneficiaries { memberId firstName lastName middleName suffix dateOfBirth gender relationship relationshipCode relationshipTypeCode individualRelationshipCode dependentSequenceNumber } } } }",
            "variables": {
                "input": {
                    "memberId": "0001234567",
                    "firstName": "ABC",
                    "lastName": "EFGH",
                    "dateOfBirth": "YYYY-MM-DD",
                    "serviceStartDate": "YYYY-MM-DD",
                    "serviceEndDate": "YYYY-MM-DD",
                    "coverageTypes": [
                        "Medical"
                    ],
                    "payerId": "12345",
                    "providerLastName": "XYZ",
                    "providerFirstName": "QWERT",
                    "providerNPI": "1234567890"
                }
            }
        }

class GraphQLResponseTransformer:
    """Transforms GraphQL responses to match REST API format"""
    
    @staticmethod
    def transform_eligibility_response(graphql_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms the GraphQL eligibility response to match the REST API format.
        This ensures the calling code receives the same structure regardless of endpoint.
        
        Args:
            graphql_response: Raw GraphQL response from Super Connector API
            
        Returns:
            Transformed response matching REST API format
        """
        try:
            # Check if GraphQL response has data
            if 'data' not in graphql_response or 'checkEligibility' not in graphql_response['data']:
                return {
                    'statuscode': '404',
                    'message': 'No eligibility data found in GraphQL response'
                }
            
            eligibility_data = graphql_response['data']['checkEligibility']['eligibility']
            if not eligibility_data:
                return {
                    'statuscode': '404',
                    'message': 'No eligibility records found'
                }
            
            # Take the first eligibility record (assuming single member query)
            first_eligibility = eligibility_data[0]
            eligibility_info = first_eligibility.get('eligibilityInfo', {})
            
            # Transform to REST-like format
            rest_response = {
                'statuscode': '200',
                'message': 'Eligibility found',
                'rawGraphQLResponse': graphql_response  # Include original response for debugging
            }
            
            # Safely extract member information
            member_info = eligibility_info.get('member', {})
            if member_info:
                rest_response.update({
                    'memberId': member_info.get('memberId'),
                    'firstName': member_info.get('firstName'),
                    'lastName': member_info.get('lastName'),
                    'middleName': member_info.get('middleName'),
                    'suffix': member_info.get('suffix'),
                    'dateOfBirth': member_info.get('dateOfBirth'),
                    'gender': member_info.get('gender'),
                    'relationship': member_info.get('relationship'),
                    'relationshipCode': member_info.get('relationshipCode'),
                    'individualRelationshipCode': member_info.get('individualRelationshipCode'),
                    'dependentSequenceNumber': member_info.get('dependentSequenceNumber')
                })
            
            # Safely extract insurance information
            insurance_info = eligibility_info.get('insuranceInfo', {})
            if insurance_info:
                rest_response.update({
                    'policyNumber': insurance_info.get('policyNumber'),
                    'eligibilityStartDate': insurance_info.get('eligibilityStartDate'),
                    'eligibilityEndDate': insurance_info.get('eligibilityEndDate'),
                    'planStartDate': insurance_info.get('planStartDate'),
                    'planEndDate': insurance_info.get('planEndDate'),
                    'policyStatus': insurance_info.get('policyStatus'),
                    'planTypeDescription': insurance_info.get('planTypeDescription'),
                    'planVariation': insurance_info.get('planVariation'),
                    'reportingCode': insurance_info.get('reportingCode'),
                    'stateOfIssueCode': insurance_info.get('stateOfIssueCode'),
                    'productType': insurance_info.get('productType'),
                    'productId': insurance_info.get('productId'),
                    'productCode': insurance_info.get('productCode'),
                    'lineOfBusiness': insurance_info.get('lineOfBusiness'),
                    'lineOfBusinessCode': insurance_info.get('lineOfBusinessCode'),
                    'coverageTypes': insurance_info.get('coverageTypes', [])
                })
            
            # Safely extract associated IDs
            associated_ids = eligibility_info.get('associatedIds', {})
            if associated_ids:
                rest_response.update({
                    'alternateId': associated_ids.get('alternateId'),
                    'medicaidRecipientId': associated_ids.get('medicaidRecipientId'),
                    'exchangeMemberId': associated_ids.get('exchangeMemberId'),
                    'alternateSubscriberId': associated_ids.get('alternateSubscriberId'),
                    'hicNumber': associated_ids.get('hicNumber'),
                    'mbiNumber': associated_ids.get('mbiNumber'),
                    'subscriberMemberFacingIdentifier': associated_ids.get('subscriberMemberFacingIdentifier'),
                    'survivingSpouseId': associated_ids.get('survivingSpouseId'),
                    'subscriberId': associated_ids.get('subscriberId'),
                    'memberReplacementId': associated_ids.get('memberReplacementId'),
                    'legacyMemberId': associated_ids.get('legacyMemberId'),
                    'customerAccountIdentifier': associated_ids.get('customerAccountIdentifier')
                })
            
            # Safely extract plan levels
            plan_levels = eligibility_info.get('planLevels', [])
            if plan_levels:
                rest_response['planLevels'] = plan_levels
            
            # Safely extract delegated info
            delegated_info = eligibility_info.get('delegatedInfo', [])
            if delegated_info:
                rest_response['delegatedInfo'] = delegated_info
            
            # Safely extract additional information
            additional_info = eligibility_info.get('additionalInfo', {})
            if additional_info:
                rest_response['isReferralRequired'] = additional_info.get('isReferralRequired')
            
            # Safely extract primary care physician
            pcp = first_eligibility.get('primaryCarePhysician', {})
            if pcp:
                rest_response.update({
                    'pcpIsFound': pcp.get('isPcpFound'),
                    'pcpLastName': pcp.get('lastName'),
                    'pcpFirstName': pcp.get('firstName'),
                    'pcpMiddleName': pcp.get('middleName'),
                    'pcpPhoneNumber': pcp.get('phoneNumber'),
                    'pcpAddress': pcp.get('address'),
                    'pcpNetworkStatusCode': pcp.get('networkStatusCode'),
                    'pcpAffiliateHospitalName': pcp.get('affiliateHospitalName'),
                    'pcpProviderGroupName': pcp.get('providerGroupName')
                })
            
            # Safely extract coordination of benefit
            cob = first_eligibility.get('coordinationOfBenefit', {})
            if cob:
                rest_response['coordinationOfBenefit'] = cob
            
            # Safely extract ID card images
            id_card_images = first_eligibility.get('idCardImages', [])
            if id_card_images:
                rest_response['idCardImages'] = id_card_images
            
            # Safely extract provider network information
            provider_network = first_eligibility.get('providerNetwork', {})
            if provider_network:
                rest_response.update({
                    'networkStatus': provider_network.get('status'),
                    'networkTier': provider_network.get('tier')
                })
            
            # Safely extract service levels
            service_levels = first_eligibility.get('serviceLevels', [])
            if service_levels:
                rest_response['serviceLevels'] = service_levels
                
                # Extract first service as example for compatibility
                if service_levels and len(service_levels) > 0:
                    first_service_level = service_levels[0]
                    individual_services = first_service_level.get('individual', [])
                    if individual_services and len(individual_services) > 0:
                        first_individual = individual_services[0]
                        services = first_individual.get('services', [])
                        if services and len(services) > 0:
                            first_service = services[0]
                            rest_response.update({
                                'serviceCode': first_service.get('serviceCode'),
                                'serviceText': first_service.get('text'),
                                'serviceStatus': first_service.get('status'),
                                'coPayAmount': first_service.get('coPayAmount'),
                                'coPayFrequency': first_service.get('coPayFrequency'),
                                'coInsurancePercent': first_service.get('coInsurancePercent'),
                                'planAmount': first_service.get('planAmount'),
                                'remainingAmount': first_service.get('remainingAmount'),
                                'metYearToDateAmount': first_service.get('metYearToDateAmount')
                            })
            
            # Safely extract extended attributes
            extended_attrs = first_eligibility.get('extendedAttributes', {})
            if extended_attrs:
                rest_response.update({
                    'fundingCode': extended_attrs.get('fundingCode'),
                    'fundingType': extended_attrs.get('fundingType'),
                    'hsa': extended_attrs.get('hsa'),
                    'cdhp': extended_attrs.get('cdhp'),
                    'governmentProgramCode': extended_attrs.get('governmentProgramCode'),
                    'cmsPackageBenefitPlanCode': extended_attrs.get('cmsPackageBenefitPlanCode'),
                    'cmsSegmentId': extended_attrs.get('cmsSegmentId'),
                    'cmsContractId': extended_attrs.get('cmsContractId'),
                    'marketType': extended_attrs.get('marketType'),
                    'obligorId': extended_attrs.get('obligorId'),
                    'marketSite': extended_attrs.get('marketSite'),
                    'benefitPlanId': extended_attrs.get('benefitPlanId'),
                    'virtualVisit': extended_attrs.get('virtualVisit'),
                    'planVariation': extended_attrs.get('planVariation'),
                    'groupNumber': extended_attrs.get('groupNumber'),
                    'legacyPanelNumber': extended_attrs.get('legacyPanelNumber'),
                    'coverageLevel': extended_attrs.get('coverageLevel'),
                    'sharedArrangement': extended_attrs.get('sharedArrangement'),
                    'productServiceCode': extended_attrs.get('productServiceCode'),
                    'designatedVirtualClinicNetwork': extended_attrs.get('designatedVirtualClinicNetwork'),
                    'medicaidVariableCode': extended_attrs.get('medicaidVariableCode'),
                    'healthInsuranceExchangeId': extended_attrs.get('healthInsuranceExchangeId'),
                    'memberDiv': extended_attrs.get('memberDiv'),
                    'legalEntityCode': extended_attrs.get('legalEntityCode')
                })
            
            # Safely extract other beneficiaries
            other_beneficiaries = first_eligibility.get('otherBeneficiaries', [])
            if other_beneficiaries:
                rest_response['otherBeneficiaries'] = other_beneficiaries
            
            return rest_response
            
        except Exception as e:
            # Log the error and the response structure for debugging
            print("Error transforming GraphQL response: {}".format(str(e)))
            print("Response structure: {}".format(json.dumps(graphql_response, indent=2)))
            return {
                'statuscode': '500',
                'message': 'Error processing GraphQL response: {}'.format(str(e)),
                'rawGraphQLResponse': graphql_response
            }

# Convenience functions for easy access
def get_eligibility_query() -> str:
    """Get the eligibility GraphQL query"""
    return GraphQLQueryBuilder.get_eligibility_query()

def build_eligibility_variables(**kwargs) -> Dict[str, Any]:
    """Build eligibility query variables"""
    return GraphQLQueryBuilder.build_eligibility_variables(**kwargs)

def build_eligibility_request(variables: Dict[str, Any]) -> Dict[str, Any]:
    """Build complete eligibility request body"""
    return GraphQLQueryBuilder.build_eligibility_request(variables)

def transform_eligibility_response(graphql_response: Dict[str, Any]) -> Dict[str, Any]:
    """Transform GraphQL eligibility response to REST format"""
    return GraphQLResponseTransformer.transform_eligibility_response(graphql_response)

def get_sample_eligibility_request() -> Dict[str, Any]:
    """Get the sample GraphQL request from swagger documentation"""
    return GraphQLQueryBuilder.get_sample_eligibility_request() 