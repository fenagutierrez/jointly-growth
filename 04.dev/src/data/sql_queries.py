"""
Reusable SQL queries for data analysis.
"""

def get_client_offer_query(client_type: str, interval_days: int) -> str:
    """
    Returns a SQL query for getting offer data based on client type and time interval.
    
    Args:
        client_type: Either 'buyer' or 'seller'
        interval_days: Number of days to look back from current date
        
    Returns:
        SQL query string
    """
    if client_type.lower() not in ['buyer', 'seller', 'landlord', 'tenant']:
        raise ValueError("client_type must be either 'buyer' or 'seller'")
        
    user_role_id = 10 if client_type.lower() == 'buyer' else (262 if client_type.lower() == 'landlord' else (257 if client_type.lower() == 'tenant' else 6))
    client_flag = ("TRUE AS buyer" if client_type.lower() == 'buyer' 
                   else "TRUE AS landlord" if client_type.lower() == 'landlord'
                   else "TRUE AS tenant" if client_type.lower() == 'tenant'
                   else "TRUE AS seller")
    
    deal_type = "Offer" if client_type.lower() in ['buyer', 'seller'] else "Lease"
    
    return f"""
    SELECT o.deal_id, o.status, o.accepted_on, {client_flag}, wd.state_or_region
    FROM tmp.offer o
    JOIN tmp.workflow_definitions wd ON o.deal_id = wd.deal_id
    WHERE o.accepted_on > NOW() - INTERVAL '{interval_days} days'
    AND wd.deal_type = '{deal_type}'
    AND o.deal_id IN (
        SELECT assignment_type_id 
        FROM tmp.user_role_assignments ura
        JOIN tmp.workflow_steps ws ON ws.deal_id = ura.assignment_type_id 
        WHERE ura.user_role_id = {user_role_id}
        AND ws.last_updated_by = ura.user_id
    )
    """

def get_client_opt_in_data(client_type: str, interval_days: int) -> str:
    """
    Returns a SQL query for getting client opt-in data based on client type and time interval.
    
    Args:
        client_type: Either 'buyer' or 'tenant'
        interval_days: Number of days to look back from current date
        
    Returns:
        SQL query string
    """
    if client_type.lower() not in ['buyer', 'tenant']:
        raise ValueError("client_type must be either 'buyer' or 'tenant'")
        
    preferences_name = 'Buyer LiveEasy Preferences' if client_type.lower() == 'buyer' else 'Buyer LiveEasy Preferences'
    
    return f"""
    SELECT ws.deal_id,
        MIN(ws.completed_on::date) AS opted_in_on,
        COUNT(1) FILTER (WHERE ws.status = 'Available') AS clients_opted_pending,
        COUNT(1) FILTER (WHERE ua.value <> 'Not interested at this time') AS clients_opted_in,
        COUNT(1) FILTER (WHERE ua.value = 'Not interested at this time') AS clients_opted_out,
        COUNT(1) FILTER (WHERE ua.value <> 'Not interested at this time' AND u.mobile_number IS NOT NULL) AS clients_opted_in_phone_number
    FROM tmp.workflow_steps ws
    LEFT JOIN tmp.user_attributes ua ON ua.source_step_id = ws.id AND ua.name = '{preferences_name}'
    LEFT JOIN tmp.users u ON ua.user_id = u.id
    WHERE ws.name ILIKE 'Select Services' 
    AND ws.created_on > NOW() - INTERVAL '{interval_days} days'
    AND ws.status <> 'Skipped'
    GROUP BY ws.deal_id
    """

def get_agent_info(agent_type: str) -> str:
    """
    Returns a SQL query for getting agent information based on agent type.
    
    Args:
        agent_type: One of 'buyer agent', 'listing agent', or 'tenant agent'
        
    Returns:
        SQL query string
    """
    if agent_type.lower() not in ['buyer agent', 'listing agent', 'tenant agent']:
        raise ValueError("agent_type must be one of: 'buyer agent', 'listing agent', 'tenant agent'")

    user_role_id = 15 if agent_type.lower() == 'buyer agent' else (
        14 if agent_type.lower() == 'listing agent' else 422)

    return f"""
    WITH ranked_roles AS (
        SELECT ura.*,
        ROW_NUMBER() OVER (PARTITION BY ura.user_id ORDER BY CASE 
            WHEN ura.user_role_id = 158 THEN 1
            WHEN ura.user_role_id = 93 THEN 2
            WHEN ura.user_role_id = 94 THEN 3
            WHEN ura.user_role_id = 92 THEN 4
            ELSE 5
        END) AS rank
        FROM tmp.user_role_assignments ura 
        WHERE ura.assignment_type = 'Partner' 
        AND ura.disabled_on IS null
    )
    SELECT DISTINCT 
        ura.assignment_type_id deal_id,
        u.id user_id,
        u.email user_email,
        tmp.get_premium_user_type(p_user_id => u.id) AS account_type,
        p.name AS team
    FROM tmp.user_role_assignments ura 
    LEFT JOIN tmp.users u ON ura.user_id = u.id
    LEFT JOIN ranked_roles rr ON rr.user_id = u.id AND rr.rank = 1
    LEFT JOIN tmp.partners p ON p.id = rr.assignment_type_id
    WHERE ura.assignment_type = 'Deal'
    AND ura.user_role_id = {user_role_id}
    """

def get_document_signed(document_type: str, client_type: str) -> str:
    """
    Returns a SQL query for getting document signing information based on document type and client type.
    
    Args:
        document_type: One of 'purchase contract', 'buyer rep', 'tenant rep', or 'exclusive right to sell'
        client_type: Type of client
        
    Returns:
        SQL query string
    """
    valid_doc_types = ['purchase contract', 'buyer rep', 'tenant rep', 'exclusive right to sell', 'lease agreement']
    if document_type.lower() not in valid_doc_types:
        raise ValueError(f"document_type must be one of: {', '.join(valid_doc_types)}")

    internal_task_name_condition = ""
    if document_type.lower() == 'purchase contract':
        internal_task_name_condition = """wt.internal_task_name in (
            select wt.internal_task_name 
            from tmp.workflow_tasks wt
            inner join tmp.workflow_definitions wd on wt.workflow_definition_id = wd.id
            where workflow_definition_id in (select id from tmp.workflow_definitions wd 
            where level_type = 'System'
            and "name" = 'Offer')
            and toolbox_category = 'Primary Contract'
        )"""
    elif document_type.lower() == 'buyer rep':
        internal_task_name_condition = "wt.internal_task_name = 'Buyer representation agreement'"
    elif document_type.lower() == 'tenant rep':
        internal_task_name_condition = "wt.internal_task_name = 'Tenant representation agreement'"
    elif document_type.lower() == 'exclusive right to sell':
        internal_task_name_condition = "wt.internal_task_name = 'Exclusive Right to Sell'"
    elif document_type.lower() == 'lease agreement':
        internal_task_name_condition = "wt.internal_task_name in ('Residential Lease Agreement', 'TXR 2001 - Residential Lease', 'Residential Lease')"


    if client_type.lower() not in ['buyer', 'seller', 'landlord', 'tenant']:
        raise ValueError("client_type must be either 'buyer' or 'seller'")
        
    user_role_id = 10 if client_type.lower() == 'buyer' else (262 if client_type.lower() == 'landlord' else (257 if client_type.lower() == 'tenant' else 6))

    return f"""
    SELECT DISTINCT ON (ws.deal_id)
        ws.deal_id,
        wt.name AS task_name,
        wt.internal_task_name,
        wt.status AS task_status,
        ws.name AS step_name,
        ws.action_type,
        ws.status AS step_status,
        ws.completed_on AS document_step_completed_on,
        ws.last_updated_on AS step_last_updated_on,
        ws.last_updated_by AS step_last_updated_by
    FROM tmp.workflow_steps ws
    INNER JOIN tmp.workflow_tasks wt ON ws.task_id = wt.id
    WHERE {internal_task_name_condition}
    AND ws.name ILIKE '%sign%'
    AND EXISTS (
        SELECT 1
        FROM jsonb_array_elements(ws.assignments) assignment
        WHERE assignment->>'userRoleId' = '{user_role_id}'
    )
    AND ws.status = 'Completed'
    """

def get_users_query(created_on_start: str) -> str:
    query = f"""
		WITH ranked_roles AS ( 
			SELECT ura.*, 
			ROW_NUMBER() OVER (PARTITION BY ura.user_id ORDER BY CASE 
			WHEN ura.user_role_id = 158 THEN 1 
			WHEN ura.user_role_id = 93 THEN 2 
			WHEN ura.user_role_id = 94 THEN 3 
			WHEN ura.user_role_id = 92 THEN 4 
			ELSE 5 
			END) AS rank 
			FROM tmp.user_role_assignments ura 
			WHERE ura.assignment_type = 'Partner' 
			AND ura.disabled_on IS NULL 
		), 
		deal_count as ( 
			WITH for_sale AS (
				WITH for_sale AS (
					SELECT ura.user_id, ur.name user_role, wd.deal_type, ura.assignment_type_id deal_id, d.created_on::date deal_created_on
					FROM (SELECT DISTINCT user_id, user_role_id, assignment_type, assignment_type_id FROM tmp.user_role_assignments) ura 
					LEFT JOIN tmp.user_roles ur ON ura.user_role_id = ur.id 
					LEFT JOIN tmp.deal d ON ura.assignment_type_id = d.id 
					LEFT JOIN tmp.workflow_definitions wd ON d.workflow_definition_id = wd.id 
					WHERE ura.assignment_type = 'Deal' 
					AND ur.name = 'Buyer Agent' 
					AND wd.deal_type IN ('Buyer', 'Offer')
					AND d.id IN (SELECT assignment_type_id FROM tmp.user_role_assignments ura, tmp.users u WHERE assignment_type = 'Deal' AND user_role_id = 10 AND u.id = ura.user_id AND u.last_login IS NOT NULL)
					UNION
					SELECT ura.user_id, ur.name user_role, wd.deal_type, ura.assignment_type_id deal_id, d.created_on::date deal_created_on
					FROM (SELECT DISTINCT user_id, user_role_id, assignment_type, assignment_type_id FROM tmp.user_role_assignments) ura 
					LEFT JOIN tmp.user_roles ur ON ura.user_role_id = ur.id 
					LEFT JOIN tmp.deal d ON ura.assignment_type_id = d.id 
					LEFT JOIN tmp.workflow_definitions wd ON d.workflow_definition_id = wd.id 
					WHERE ura.assignment_type = 'Deal'  
					AND ur.name = 'Listing Agent' 
					AND wd.deal_type IN ('Seller', 'Offer')
					AND d.id IN (SELECT assignment_type_id FROM tmp.user_role_assignments ura, tmp.users u WHERE assignment_type = 'Deal' AND user_role_id = 6 AND u.id = ura.user_id AND u.last_login IS NOT NULL)
				)
				SELECT fs.user_id, 
				COUNT(fs.deal_id) for_sale_count,
				COUNT(CASE WHEN fs.deal_created_on >= CURRENT_DATE - INTERVAL '7 days' THEN fs.deal_id END) as for_sale_count_last_7_days,
				COUNT(CASE WHEN fs.deal_created_on >= CURRENT_DATE - INTERVAL '30 days' THEN fs.deal_id END) as for_sale_count_last_30_days
				FROM for_sale fs
				GROUP BY fs.user_id
			),
			for_rent AS (
				WITH for_rent AS (
					SELECT ura.user_id, ur.name user_role, wd.deal_type, ura.assignment_type_id deal_id, d.created_on::date deal_created_on
					FROM (SELECT DISTINCT user_id, user_role_id, assignment_type, assignment_type_id FROM tmp.user_role_assignments) ura 
					LEFT JOIN tmp.user_roles ur ON ura.user_role_id = ur.id 
					LEFT JOIN tmp.deal d ON ura.assignment_type_id = d.id 
					LEFT JOIN tmp.workflow_definitions wd ON d.workflow_definition_id = wd.id 
					WHERE ura.assignment_type = 'Deal'  
					AND ur.name = 'Tenant Agent' 
					AND wd.deal_type IN ('Tenant', 'Lease')
					AND d.id IN (SELECT assignment_type_id FROM tmp.user_role_assignments ura, tmp.users u WHERE assignment_type = 'Deal' AND user_role_id = 257 AND u.id = ura.user_id AND u.last_login IS NOT NULL)
					UNION
					SELECT ura.user_id, ur.name user_role, wd.deal_type, ura.assignment_type_id deal_id, d.created_on::date deal_created_on
					FROM (SELECT DISTINCT user_id, user_role_id, assignment_type, assignment_type_id FROM tmp.user_role_assignments) ura 
					LEFT JOIN tmp.user_roles ur ON ura.user_role_id = ur.id 
					LEFT JOIN tmp.deal d ON ura.assignment_type_id = d.id 
					LEFT JOIN tmp.workflow_definitions wd ON d.workflow_definition_id = wd.id 
					WHERE ura.assignment_type = 'Deal'  
					AND ur.name = 'Listing Agent' 
					AND wd.deal_type IN ('Landlord', 'Lease')
					AND d.id IN (SELECT assignment_type_id FROM tmp.user_role_assignments ura, tmp.users u WHERE assignment_type = 'Deal' AND user_role_id = 262 AND u.id = ura.user_id AND u.last_login IS NOT NULL)
				)
				SELECT fr.user_id, 
				COUNT(fr.deal_id) for_rent_count,
				COUNT(CASE WHEN fr.deal_created_on >= CURRENT_DATE - INTERVAL '7 days' THEN fr.deal_id END) AS for_rent_count_last_7_days,
				COUNT(CASE WHEN fr.deal_created_on >= CURRENT_DATE - INTERVAL '30 days' THEN fr.deal_id END) AS for_rent_count_last_30_days
				FROM for_rent fr
				GROUP BY fr.user_id
			)
			SELECT for_sale.user_id, for_sale_count, for_sale_count_last_7_days, for_sale_count_last_30_days, for_rent_count, for_rent_count_last_7_days, for_rent_count_last_30_days
			FROM for_sale 
			LEFT JOIN for_rent ON for_sale.user_id = for_rent.user_id
		) 
		SELECT u.id user_id, 
		u.email user_email,
		TRIM(LEADING '0' FROM ua.value::json->> 'mlsMemberId') as user_license,
		u.status user_status, 
		tmp.get_premium_user_type(p_user_id => u.id) AS user_account_type, 
		u.primary_user_type primary_user_type, 
		u.first_name user_first_name, 
		u.last_name user_last_name, 
		u.mobile_number user_mobile_number, 
		u.created_on::DATE user_created_on, 
		ur.name AS user_team_role, 
		u.state user_state,
		p.id AS user_partner_id, 
		p.name AS user_team, 
		dc.*,
        ua_orig.value as user_origination_source
		FROM tmp.users u 
		LEFT JOIN ranked_roles rr ON rr.user_id = u.id AND rr.rank = 1 
		LEFT JOIN tmp.user_roles ur ON ur.id = rr.user_role_id 
		LEFT JOIN tmp.partners p ON p.id = rr.assignment_type_id 
		LEFT JOIN deal_count dc ON dc.user_id = u.id 
		LEFT JOIN tmp.user_attributes ua on u.id = ua.user_id and ua.name = 'MLS Member ID' and ua.valid_to isnull
        left join tmp.user_attributes ua_orig on u.id = ua_orig.user_id and ua_orig.name ilike '%User Origination Source%' and ua_orig.valid_to is null
		WHERE u.primary_user_type <> 'Client' 
		AND u.created_on::date >= '{created_on_start}'
		ORDER BY u.created_on desc
    """
    return query


AGENT_INFO_QUERY = """
WITH ranked_roles AS ( 
    SELECT ura.*, 
    ROW_NUMBER() OVER (PARTITION BY ura.user_id ORDER BY CASE 
    WHEN ura.user_role_id = 158 THEN 1 
    WHEN ura.user_role_id = 93 THEN 2 
    WHEN ura.user_role_id = 94 THEN 3 
    WHEN ura.user_role_id = 92 THEN 4 
    ELSE 5 
    END) AS rank 
    FROM tmp.user_role_assignments ura 
    WHERE ura.assignment_type = 'Partner' 
    AND ura.disabled_on IS NULL 
)
SELECT u.id, 
u.email,
TRIM(LEADING '0' FROM ua.value::json->> 'mlsMemberId') as jointly_agent_license,
u.status, 
tmp.get_premium_user_type(p_user_id => u.id) AS account_type, 
u.primary_user_type, 
u.first_name, 
u.last_name, 
u.mobile_number, 
u.created_on::DATE AS created_on, 
ur.name AS team_role, 
u.state,
p.id AS team_id, 
p.name AS team,
p.finance_center_empty_state_enabled
FROM tmp.users u 
LEFT JOIN ranked_roles rr ON rr.user_id = u.id AND rr.rank = 1 
LEFT JOIN tmp.user_roles ur ON ur.id = rr.user_role_id 
LEFT JOIN tmp.partners p ON p.id = rr.assignment_type_id  
LEFT JOIN tmp.user_attributes ua on u.id = ua.user_id and ua.name = 'MLS Member ID' and ua.valid_to isnull
WHERE u.primary_user_type <> 'Client' 
ORDER BY u.created_on desc
""" 


PURCHASE_CONTRACT_QUERY = """
SELECT DISTINCT ON (ws.deal_id)
    ws.deal_id,
    wt.name AS task_name,
    wt.internal_task_name,
    wt.status AS task_status,
    ws.name AS step_name,
    ws.action_type,
    ws.status AS step_status,
    ws.completed_on AS purchase_contract_step_completed_on,
    ws.last_updated_on AS step_last_updated_on,
    ws.last_updated_by AS step_last_updated_by
FROM tmp.workflow_steps ws
INNER JOIN tmp.workflow_tasks wt ON ws.task_id = wt.id
WHERE wt.internal_task_name in (
        select wt.internal_task_name 
        from tmp.workflow_tasks wt
        inner join tmp.workflow_definitions wd on wt.workflow_definition_id = wd.id
        where workflow_definition_id in (select id from tmp.workflow_definitions wd 
        where level_type = 'System'
        and "name" = 'Offer')
        and toolbox_category = 'Primary Contract'
)
AND ws.name ILIKE '%sign%'
AND EXISTS (
    SELECT 1
    FROM jsonb_array_elements(ws.assignments) assignment
    WHERE assignment->>'userRoleId' = '10'
)
AND ws.status = 'Completed'
"""

def get_users_with_deals_query() -> str:
    """
    Returns the main users query with deal counts and user information.
    This is the comprehensive query used for user synchronization.
    
    Returns:
        SQL query string for fetching user data with deal counts
    """
    return """
		WITH ranked_roles AS ( 
			SELECT ura.*, 
			ROW_NUMBER() OVER (PARTITION BY ura.user_id ORDER BY CASE 
			WHEN ura.user_role_id = 158 THEN 1 
			WHEN ura.user_role_id = 93 THEN 2 
			WHEN ura.user_role_id = 94 THEN 3 
			WHEN ura.user_role_id = 92 THEN 4 
			ELSE 5 
			END) AS rank 
			FROM tmp.user_role_assignments ura 
			WHERE ura.assignment_type = 'Partner' 
			AND ura.disabled_on IS NULL 
		), 
		deal_count as ( 
			WITH for_sale AS (
				WITH for_sale AS (
					SELECT ura.user_id, ur.name user_role, wd.deal_type, ura.assignment_type_id deal_id, d.created_on::date deal_created_on
					FROM (SELECT DISTINCT user_id, user_role_id, assignment_type, assignment_type_id FROM tmp.user_role_assignments) ura 
					LEFT JOIN tmp.user_roles ur ON ura.user_role_id = ur.id 
					LEFT JOIN tmp.deal d ON ura.assignment_type_id = d.id 
					LEFT JOIN tmp.workflow_definitions wd ON d.workflow_definition_id = wd.id 
					WHERE ura.assignment_type = 'Deal' 
					AND ur.name = 'Buyer Agent' 
					AND wd.deal_type IN ('Buyer', 'Offer')
					AND d.id IN (SELECT assignment_type_id FROM tmp.user_role_assignments ura, tmp.users u WHERE assignment_type = 'Deal' AND user_role_id = 10 AND u.id = ura.user_id AND u.last_login IS NOT NULL)
					UNION
					SELECT ura.user_id, ur.name user_role, wd.deal_type, ura.assignment_type_id deal_id, d.created_on::date deal_created_on
					FROM (SELECT DISTINCT user_id, user_role_id, assignment_type, assignment_type_id FROM tmp.user_role_assignments) ura 
					LEFT JOIN tmp.user_roles ur ON ura.user_role_id = ur.id 
					LEFT JOIN tmp.deal d ON ura.assignment_type_id = d.id 
					LEFT JOIN tmp.workflow_definitions wd ON d.workflow_definition_id = wd.id 
					WHERE ura.assignment_type = 'Deal'  
					AND ur.name = 'Listing Agent' 
					AND wd.deal_type IN ('Seller', 'Offer')
					AND d.id IN (SELECT assignment_type_id FROM tmp.user_role_assignments ura, tmp.users u WHERE assignment_type = 'Deal' AND user_role_id = 6 AND u.id = ura.user_id AND u.last_login IS NOT NULL)
				)
				SELECT fs.user_id, 
				COUNT(fs.deal_id) for_sale_count,
				COUNT(CASE WHEN fs.deal_created_on >= CURRENT_DATE - INTERVAL '7 days' THEN fs.deal_id END) as for_sale_count_last_7_days,
				COUNT(CASE WHEN fs.deal_created_on >= CURRENT_DATE - INTERVAL '30 days' THEN fs.deal_id END) as for_sale_count_last_30_days
				FROM for_sale fs
				GROUP BY fs.user_id
			),
			for_rent AS (
				WITH for_rent AS (
					SELECT ura.user_id, ur.name user_role, wd.deal_type, ura.assignment_type_id deal_id, d.created_on::date deal_created_on
					FROM (SELECT DISTINCT user_id, user_role_id, assignment_type, assignment_type_id FROM tmp.user_role_assignments) ura 
					LEFT JOIN tmp.user_roles ur ON ura.user_role_id = ur.id 
					LEFT JOIN tmp.deal d ON ura.assignment_type_id = d.id 
					LEFT JOIN tmp.workflow_definitions wd ON d.workflow_definition_id = wd.id 
					WHERE ura.assignment_type = 'Deal'  
					AND ur.name = 'Tenant Agent' 
					AND wd.deal_type IN ('Tenant', 'Lease')
					AND d.id IN (SELECT assignment_type_id FROM tmp.user_role_assignments ura, tmp.users u WHERE assignment_type = 'Deal' AND user_role_id = 257 AND u.id = ura.user_id AND u.last_login IS NOT NULL)
					UNION
					SELECT ura.user_id, ur.name user_role, wd.deal_type, ura.assignment_type_id deal_id, d.created_on::date deal_created_on
					FROM (SELECT DISTINCT user_id, user_role_id, assignment_type, assignment_type_id FROM tmp.user_role_assignments) ura 
					LEFT JOIN tmp.user_roles ur ON ura.user_role_id = ur.id 
					LEFT JOIN tmp.deal d ON ura.assignment_type_id = d.id 
					LEFT JOIN tmp.workflow_definitions wd ON d.workflow_definition_id = wd.id 
					WHERE ura.assignment_type = 'Deal'  
					AND ur.name = 'Listing Agent' 
					AND wd.deal_type IN ('Landlord', 'Lease')
					AND d.id IN (SELECT assignment_type_id FROM tmp.user_role_assignments ura, tmp.users u WHERE assignment_type = 'Deal' AND user_role_id = 262 AND u.id = ura.user_id AND u.last_login IS NOT NULL)
				)
				SELECT fr.user_id, 
				COUNT(fr.deal_id) for_rent_count,
				COUNT(CASE WHEN fr.deal_created_on >= CURRENT_DATE - INTERVAL '7 days' THEN fr.deal_id END) AS for_rent_count_last_7_days,
				COUNT(CASE WHEN fr.deal_created_on >= CURRENT_DATE - INTERVAL '30 days' THEN fr.deal_id END) AS for_rent_count_last_30_days
				FROM for_rent fr
				GROUP BY fr.user_id
			)
			SELECT for_sale.user_id, for_sale_count, for_sale_count_last_7_days, for_sale_count_last_30_days, for_rent_count, for_rent_count_last_7_days, for_rent_count_last_30_days
			FROM for_sale 
			LEFT JOIN for_rent ON for_sale.user_id = for_rent.user_id
		) 
		SELECT u.id, 
		u.email,
        source.value source,
		TRIM(LEADING '0' FROM ua.value::json->> 'mlsMemberId') as jointly_agent_license,
		u.status, 
		tmp.get_premium_user_type(p_user_id => u.id) AS account_type, 
		u.primary_user_type, 
		u.first_name, 
		u.last_name, 
		u.mobile_number, 
		u.created_on::DATE AS created_on, 
		ur.name AS team_role, 
		u.state,
		p.id AS partner_id, 
		p.name AS team, 
		dc.* 
		FROM tmp.users u 
		LEFT JOIN ranked_roles rr ON rr.user_id = u.id AND rr.rank = 1 
		LEFT JOIN tmp.user_roles ur ON ur.id = rr.user_role_id 
		LEFT JOIN tmp.partners p ON p.id = rr.assignment_type_id 
		LEFT JOIN deal_count dc ON dc.user_id = u.id 
		LEFT JOIN tmp.user_attributes ua on u.id = ua.user_id and ua.name = 'MLS Member ID' and ua.valid_to isnull
        LEFT JOIN tmp.user_attributes source on u.id = source.user_id and source.name = 'User Origination Source' and ua.valid_to isnull
		WHERE u.primary_user_type <> 'Client' 
		ORDER BY u.created_on desc
"""

def get_login_counts_query() -> str:
    """
    Returns the login counts query for tracking user login activity.
    
    Returns:
        SQL query string for fetching login data
    """
    return """
SELECT
    ala.email,
    DATE_TRUNC('month', ala.created_on AT TIME ZONE 'UTC' AT TIME ZONE 'America/Chicago')::DATE AS login_month,
    COUNT(ala.id) AS number_of_logins
FROM
    tmp.audit_login_attempts AS ala
WHERE
    ala.login_result = 'Validated'
    AND ala.ip_address NOT IN (
        SELECT DISTINCT ip_address 
        FROM tmp.audit_login_attempts 
        WHERE email ILIKE '%Jointly%' OR email ILIKE '%cyberbacker%'
    )
    AND (ala.created_on AT TIME ZONE 'UTC' AT TIME ZONE 'America/Chicago') >= '2025-01-01'
GROUP BY
    ala.email,
    login_month
ORDER BY
    login_month DESC,
    number_of_logins DESC;
"""

def get_teams_with_onboarding_query() -> str:
    """
    Returns the teams query with onboarding deal information.
    This query fetches team/partner data along with their deal information.
    
    Returns:
        SQL query string for fetching team data with onboarding deals
    """
    return """
	with onboarding_deal as ( 
	SELECT 
	deal_id, 
	d.partner_id, 
	MAX(CASE WHEN ddv.name = 'Contact Email' THEN value END) AS contact_email, 
	MAX(CASE WHEN ddv.name = 'Fee' THEN value END) AS fee, 
	MAX(CASE WHEN ddv.name = 'Fee Frequency' THEN value END) AS fee_frequency, 
	MAX(CASE WHEN ddv.name = 'License Type' THEN value END) AS license_type, 
	MAX(CASE WHEN ddv.name = 'User Count' THEN value END) AS user_count 
	FROM tmp.deal_data_values ddv 
	left join tmp.deal d 
	on ddv.deal_id = d.id 
	WHERE ddv.deal_id in (select id from tmp.deal where partner_id notnull) 
	AND ddv.name IN ('Contact Email','Fee', 'Fee Frequency', 'License Type', 'User Count') 
	AND ddv.valid_to IS NULL 
	GROUP BY ddv.deal_id, d.partner_id 
) 
select distinct p.id, p.name, p.status, p.created_on::date, od.fee, od.fee_frequency, od.user_count, od.contact_email 
from tmp.partners p 
left join onboarding_deal od on p.id = od.partner_id 
order by p.id
"""

def get_mortgage_leads_query() -> str:
    """
    Returns the mortgage leads query with best deal information.
    This query fetches mortgage leads data along with user and deal information.
    
    Returns:
        SQL query string for fetching mortgage leads data
    """
    return """
WITH BestDealForUser AS (
SELECT
    ranked_deals.user_id,
    ranked_deals.deal_id
FROM (
    -- This inner query ranks all deals for each user
    SELECT
        ura.user_id,
        d.id AS deal_id,
        ROW_NUMBER() OVER(
            PARTITION BY ura.user_id
            ORDER BY
                CASE d.status
                    WHEN 'Pending' THEN 1
                    WHEN 'Active' THEN 2
                    WHEN 'Onboarding' THEN 3
                    ELSE 4
                END,
                d.created_on DESC
        ) AS rn
    FROM
        tmp.user_role_assignments AS ura
    JOIN
        tmp.user_roles AS ur ON ura.user_role_id = ur.id
    JOIN
        tmp.deal AS d ON ura.assignment_type_id = d.id
    LEFT JOIN 
        tmp.workflow_definitions wd ON d.id = wd.deal_id
    WHERE
        ura.assignment_type = 'Deal'
        AND ur.name ILIKE '%Buyer%'
        AND d.archived_on IS NULL
        AND wd.deal_type = 'Buyer'
) AS ranked_deals
WHERE rn = 1 -- Filter to get only the #1 ranked deal for each user
)
-- Main query to get the final deal_id
SELECT
ml.id lead_id,
ml.user_id,
COALESCE(ml.deal_id, bdfu.deal_id) AS deal_id,
(ml.created_on AT TIME ZONE 'UTC' AT TIME ZONE 'America/Chicago')::date created_on,
ml.mortgage_partner_lender_id,
ml.lead_type,
ml.ignore_for_reporting,
u.email,
u.first_name,
u.last_name
FROM
tmp.mortgage_leads AS ml
LEFT JOIN
BestDealForUser AS bdfu ON ml.user_id = bdfu.user_id
left join tmp.users u on u.id = ml.user_id
order by ml.created_on asc
"""

def get_jointly_users_mls_query(mls_definition_id: str = '852') -> str:
    """
    Returns a SQL query for fetching Jointly users with MLS data.
    
    Args:
        mls_definition_id: The MLS definition ID to filter by (default: '852')
        
    Returns:
        SQL query string for fetching Jointly users with MLS data
    """
    return f"""
    select distinct u.id user_id, u.email, u.first_name, u.last_name, u.created_on::date user_created_on, 
    TRIM(LEADING '0' FROM ua.value::json->> 'mlsMemberId') as jointly_agent_license, 
    TRIM(LEADING '0' FROM ua.value::json->> 'mlsDefinitionId') as mls_definition_id
    from tmp.users u 
    left join tmp.user_attributes ua 
    on ua.user_id = u.id 
    and ua.name = 'MLS Member ID' 
    and ua.valid_to isnull 
    where u.primary_user_type <> 'Client' 
    and TRIM(LEADING '0' FROM ua.value::json->> 'mlsMemberId') notnull
    and TRIM(LEADING '0' FROM ua.value::json->> 'mlsDefinitionId') = '{mls_definition_id}'
    order by u.id desc 
    """

def get_mls_choice_members_query(mls_definition_id: str = '852', member_types: list = None) -> str:
    """
    Returns a SQL query for fetching MLS Choice members.
    
    Args:
        mls_definition_id: The MLS definition ID to filter by (default: '852')
        member_types: List of member types to filter by (default: ['MLS Only Salesperson', 'MLS Only Broker'])
        
    Returns:
        SQL query string for fetching MLS Choice members
    """
    if member_types is None:
        member_types = ['MLS Only Salesperson', 'MLS Only Broker']
    
    member_types_str = "', '".join(member_types)
    return f"""
    select *
    from mls."member" m 
    where mls_definition_id = {mls_definition_id} 
    and m.member_type in ('{member_types_str}')
    and m.state_license notnull 
    order by 2 desc
    """

def get_unique_login_count_query(start_date: str, end_date: str) -> str:
    """
    Returns a SQL query for counting unique users who logged in within a specific date range.
    
    Args:
        start_date: Start date string (YYYY-MM-DD or DD-MON-YYYY)
        end_date: End date string (YYYY-MM-DD or DD-MON-YYYY)
        
    Returns:
        SQL query string
    """
    return f"""
    select count(distinct u.email) 
    from tmp.audit_login_attempts ala, tmp.users u
    where login_result = 'Validated'
    and u.email = ala.email
    and u.primary_user_type <> 'Client'
    and u.email not ilike '%jointly%'
    and u.email not ilike 'cyberbacker'
    and ala.created_on::date between '{start_date}' and '{end_date}'
    """

def get_cba_referrals_query() -> str:
    """
    Returns the SQL query for CB&A Referrals export.
    
    Returns:
        SQL query string
    """
    return """
WITH 
-- 1. Pivot Agents: Get one row per deal with both agent IDs
pivoted_agents AS (
    SELECT 
        ura.assignment_type_id AS deal_id, 
        MAX(CASE WHEN ura.user_role_id = 14 THEN ura.user_id END) AS listing_agent_id,
        MAX(CASE WHEN ura.user_role_id = 15 THEN ura.user_id END) AS buyer_agent_id
    FROM tmp.user_role_assignments ura 
    WHERE ura.assignment_type = 'Deal'
      AND ura.user_role_id IN (14, 15)
      AND ura.disabled_on IS NULL
    GROUP BY ura.assignment_type_id
), 
-- 2. Pivot Data Values: Get Referral, Address, Date AND Created Date
pivoted_data AS (
    SELECT 
        ddv.deal_id, 
        MAX(CASE WHEN ddv.name = 'CBA Agent Referral' THEN ddv.value END)      AS referral_value,
        MAX(CASE WHEN ddv.name = 'CBA Agent Referral' THEN ddv.created_on END) AS referral_created_on,
        MAX(CASE WHEN ddv.name = 'Property Address'   THEN ddv.value END)      AS property_address
    FROM tmp.deal_data_values ddv
    WHERE ddv.name IN ('CBA Agent Referral', 'Property Address')
    GROUP BY ddv.deal_id
)
-- 3. Final Selection: Join Users, Parse, and Format
SELECT 
    d.id,
    pa.listing_agent_id,
    TRIM(ul.first_name || ' ' || ul.last_name) AS listing_agent_name,
    ul.email AS listing_agent_email,
    -- Buyer Agent Details (Joined via ub alias)
    pa.buyer_agent_id,
    TRIM(ub.first_name || ' ' || ub.last_name) AS buyer_agent_name,
    ub.email AS buyer_agent_email,
    -- Deal Data
    pd.property_address::json ->> 'fullAddress' AS "Property Address",
    -- Referral Columns
    pd.referral_created_on::date AS "Referral Created Date", -- Cast to date as requested
    TRIM(SPLIT_PART(SPLIT_PART(pd.referral_value, '.', 1), '?', 2)) AS "Recommends",
    TRIM(SPLIT_PART(pd.referral_value, 'Why?', 2)) AS "Why"
FROM pivoted_data pd
LEFT JOIN pivoted_agents pa ON pd.deal_id = pa.deal_id
LEFT JOIN tmp.deal d ON pd.deal_id = d.id
-- Join users table for Listing Agent
LEFT JOIN tmp.users ul ON pa.listing_agent_id = ul.id
-- Join users table for Buyer Agent
LEFT JOIN tmp.users ub ON pa.buyer_agent_id = ub.id
WHERE pd.referral_value IS NOT null
order by pd.referral_created_on
    """