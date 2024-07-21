def get_activities_no_passed_sina_bc() -> str:
    return """
  WITH CTE_ProfesionalInformado AS (
      SELECT 
          apce.PROC_ID,
          proff.PROF_FULL_NAME AS 'PROFESIONAL INFORMADO'
      FROM [sinasuite].[dbo].[APPR_COMPLETED_EXPLORATIONS] apce
      INNER JOIN [sinasuite].[dbo].[ORMA_PROFESSIONALS] proff ON proff.PROF_ID = apce.PROF_ID_INFORMER
      WHERE apce.APCE_DELETED = 0
  )

  SELECT
  cent.CENT_NAME AS [CENTER],
  aa.APPO_START_DATE AS [APPOINTMENT DATE],
  inna.INNA_NAME AS [INSURANCE],
  coll.COLL_NAME AS [COLLECTIVE],
  pati.PATI_CLINICAL_HISTORY_ID AS [NHC],
  epis.EPIS_CODE AS [EPISODE CODE],
  pati.PATI_FULL_NAME AS [PATIENT],
  bene.BENE_CODE AS [BENEFIT CODE],
  bene.BENE_NAME AS [BENEFIT NAME],
  CONCAT(idty.IDTY_DESCRIPTION_ES, ': ', pity.PITY_VALUE) AS [IDENTIFIER],
  acti.ACTI_AUTHORIZATION_LEVEL AS [AUTHORIZATION LEVEL],
  apts.PTST_DESCRIPTION_ES AS [PROPOSAL STATE],
  acti_state.ACST_DESCRIPTION_ES AS [ACTIVITY STATE],
  prof.PROF_FULL_NAME AS [PROFESSIONAL REALIZED],
  CTE_ProfesionalInformado.[PROFESIONAL INFORMADO] AS [PROFESSIONAL INFORMED],
  pp.PROC_CODE AS [PROCEDURE CODE]
  FROM [sinasuite].[dbo].[ACTI_ACTIVITIES] acti
  LEFT OUTER JOIN [sinasuite].[dbo].[ERP_Actividad] a on a.IdRegistroHIS = acti.ACTI_CODE COLLATE Modern_Spanish_CI_AI
  INNER JOIN [sinasuite].[dbo].[PROC_PROCEDURES] pp ON pp.PROC_ID = acti.PROC_ID 
  INNER JOIN [sinasuite].[dbo].[PROC_RAYS] pr ON pr.PROC_ID = pp.PROC_ID
  INNER JOIN [sinasuite].[dbo].[PROC_RAY_TESTS] prt ON prt.PRAY_ID = pr.PRAY_ID AND prt.TTST_ID NOT IN (3, 4)
  INNER JOIN [sinasuite].[dbo].[TEST_TESTS] tt ON tt.TEST_ID = prt.TEST_ID AND tt.TEST_DELETED = 0
  INNER JOIN [sinasuite].[dbo].[APPO_APPO_PROCEDURES] aap ON aap.PROC_ID = pp.PROC_ID 
  INNER JOIN [sinasuite].[dbo].[APPO_APPOINTMENTS] aa ON aa.APPO_ID = aap.APPO_ID AND aa.STAT_ID IN (3, 4)
  INNER JOIN [sinasuite].[dbo].[APPO_PROPOSALS] ap ON ap.APPR_ID = pp.APPR_ID AND ap.PPTY_ID = 3
  INNER JOIN [sinasuite].[dbo].[APPO_PROPOSAL_TYPE_STATES] apts ON apts.PRST_ID = ap.PRST_ID AND apts.PPTY_ID = ap.PPTY_ID
  INNER JOIN [sinasuite].[dbo].[ORMA_PROFESSIONALS] prof ON prof.PROF_ID = aa.PROF_ID_FINISH_PATIENT_CARE
  INNER JOIN [sinasuite].[dbo].[ACTI_ACTIVITY_STATES] acti_state ON acti_state.ACST_ID = acti.ACST_ID
  INNER JOIN [sinasuite].[dbo].[ORMA_CENTERS] cent ON cent.CENT_ID = acti.CENT_ID AND CENT_DELETED = 0
  INNER JOIN [sinasuite].[dbo].[EPIS_EPISODES] epis ON epis.EPIS_ID = acti.EPIS_ID AND EPIS_DELETED = 0
  INNER JOIN [sinasuite].[dbo].[ORMA_BENEFITS] bene ON bene.BENE_ID = tt.BENE_ID AND bene.BENE_ACTIVE = 1 AND bene.BENE_DELETED = 0 AND bene.BILLABLE = 1
  INNER JOIN [sinasuite].[dbo].[PATI_PATIENTS] pati ON pati.PATI_ID = acti.PATI_ID AND PATI_ACTIVE = 1 AND pati.PATI_ID NOT IN (2, 3)
  INNER JOIN [sinasuite].[dbo].[PATI_PATIENT_IDENTIFICATIONS] pity ON pity.PATI_ID = acti.PATI_ID AND pity.PITY_DEFAULT = 1
  INNER JOIN [sinasuite].[dbo].[PARA_IDENTIFICATION_TYPES] idty ON idty.IDTY_ID = pity.IDTY_ID AND idty.IDTY_DELETED = 0
  INNER JOIN [sinasuite].[dbo].[GARA_COLLECTIVES] coll ON coll.COLL_ID = acti.COLL_ID AND coll.COLL_DELETED = 0
  INNER JOIN [sinasuite].[dbo].[GARA_INSURANCES] inna ON inna.INNA_ID = coll.INNA_ID AND inna.INNA_DELETED = 0
  LEFT OUTER JOIN CTE_ProfesionalInformado ON CTE_ProfesionalInformado.PROC_ID = acti.PROC_ID
  WHERE acti.ACTI_DELETED = 0 AND a.IdRegistroHIS is NULL
  """


def get_integrations_error_per_patient() -> str:
    return f"""
  SELECT
  iii.INTI_CODE AS [MESSAGE CODE],
  iii.INTI_CREATED_DATE AS [MESSAGE CREATED],
  CASE
    WHEN iii.INME_ID = 23 THEN 'Mensaje de Imagen'
    WHEN iii.INME_ID = 64 THEN 'Mensaje de Informada'
    ELSE NULL
  END AS [MESSAGE TYPE],
  iii.INTI_ERROR AS [ERROR MESSAGE]
  FROM [sinasuite].[dbo].[INTE_INTEGRATIONS_INPUT] iii
  WHERE iii.INME_ID IN (23, 64) AND iii.INTI_STATUS = 5 
  AND JSON_VALUE(iii.INTI_MSG, '$.patient.identifiers[0].id') = ?
  AND JSON_VALUE(iii.INTI_MSG, '$.order.fillOrderNumber') = ?
  """
