USE [sinasuite]
SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;

BEGIN

Declare @beneCode as nvarchar(50) 			-- Código de prestación
Declare @beneDescription as nvarchar(300)	-- Descripción de la prestación
Declare @betyCode as nvarchar(50)				-- Código de familia	(tipo de prestación)
Declare @bestCode as nvarchar(50)			-- Código de subfamilia (subtipo de prestación)
Declare @active as bit
Declare @unit as nvarchar(20)						-- unidad de medida


Declare @ppty_ids as SINA_List;		-- Código de tipo de prestación (Indica el tipo de solicitud a aplicar la prestación)
Declare @proposalWithTest as SINA_List;
Declare @checkUpdate as bit;
Declare @error as nvarchar(2000) = ''

Declare @bene_id as bigint = null;
Declare @test_id as bigint = null;
Declare @isTest as int=0;


---------------------------
-- Configuration
---------------------------

DECLARE @PRESTACIONES AS TABLE (
beneCode NVARCHAR(50)
,beneDescription NVARCHAR(300)
,betyCode NVARCHAR(50)
,bestCode NVARCHAR(50)
,active INT
,unit NVARCHAR(20)
,pptyIds NVARCHAR(250)
);


INSERT INTO @PRESTACIONES (beneCode,beneDescription,betyCode,bestCode,active,unit,pptyIds)
(SELECT IDPRESTACION,
		DESCRIPCION,
		IDFAMILIA,
		IDSUBFAMILIA,
		ACTIVO,
		UNIDADMEDIDA,
		(SELECT TOP 1 CONCAT(STUFF(
				(SELECT ','+CONVERT(VARCHAR(10),ppty_Id) AS [text()]
					FROM PROP_PROP_TYPE_BENEFIT_TYPES PPTBT
					INNER JOIN ORMA_BENEFIT_TYPES OBT ON OBT.BETY_ID=PPTBT.BETY_ID AND OBT.BETY_CODE=IDFAMILIA COLLATE Modern_Spanish_CI_AS
					FOR XML PATH('')), 1, 1, ''),'')
				FROM PROP_PROP_TYPE_BENEFIT_TYPES T) as proposalTypesList

FROM ERP_PRESTACION EP
WHERE EP.FLEIDO IS NULL AND EP.DESCRIPCION IS NOT NULL AND EP.IDFAMILIA IS NOT NULL AND IDPRESTACION IN ({values_idprestaciones}))

-- Tabla para guardar los tipos de propuestas que requieren de test en sina.
INSERT INTO @proposalWithTest (id) SELECT PPTY_ID FROM PROP_PROPOSAL_TYPES WHERE PPTY_REQUIRED_TEST=1

-- Comenzamos a recorrer la tabla temporal
	WHILE EXISTS (SELECT TOP 1 * FROM @PRESTACIONES)
	BEGIN

	-- Esta será la acción que estamos realizando: 1 Creación, 2 Modificación 3 eliminación.
			Declare @action int;

			Declare @ppty_ids_string NVARCHAR(250);

			DELETE from @ppty_ids;

			set @bene_id=null;
			set @test_id=null;
			set @isTest=0;

			SELECT TOP 1 @beneCode=beneCode,@beneDescription=beneDescription,@betyCode=betyCode,@bestCode=bestCode,@active=active,@unit=unit,@ppty_ids_string=pptyIds
				FROM @PRESTACIONES;

			INSERT INTO @ppty_ids (id) (SELECT id FROM [dbo].SplitString(@ppty_ids_string, ','))

			if not exists (select top 1 *
								from ORMA_BENEFIT_TYPES BT
									inner join  ORMA_BENEFIT_SUBTYPES BST on BT.BETY_ID = BST.BETY_ID
								where BT.BETY_CODE = @betyCode and BST.BEST_CODE = @bestCode)
			begin
				set @error = FORMATMESSAGE(N'Family or subfamily not exists (CODE: %s, FAMILY: %s, SUBFAMILY: %s).', @beneCode, @betyCode, @bestCode)
				exec [PROC_SET_ERROR_NOTIFICATIONS] @beneCode, 'Benefit', 'E003', @error

				DELETE TOP (1) FROM @PRESTACIONES;

				CONTINUE;
			end

		BEGIN TRY
		-- Iniciamos una transacción por si hubiera que ejecutar un rollback
			BEGIN TRAN T1

			SELECT DISTINCT @bene_id=BENE_ID FROM ORMA_BENEFITS WHERE BENE_CODE=@beneCode


			IF (@active = 1 or @active is null)
			BEGIN

		--Si no existe un registro previo de la prestación será una creación, sino será una modificación.
				IF (@bene_id is null)
				BEGIN
					set @action=1;
				END
				ELSE
				BEGIN
					set @action=2;
				END

			END
			ELSE
				BEGIN
					set @action=3;
				END

		--Chequeamos si existe alguna actividad o petición que contenga esta prestación para el caso en que estemos borrándola o actualizándo su familia
		if (@action=2 or @action=3)
		begin
			if  exists (select AC.ACTI_ID
										from ACTI_ACTIVITIES AC
										where
											AC.ACST_ID not in (4, 6) --Processed, Not Invoiced
											and AC.ACTI_DELETED = 0
											and AC.BENE_ID = @bene_id)
					begin
						set @error = FORMATMESSAGE(N'Has pending activity (UPDATE-CODE: %s)', @beneCode)
						exec [PROC_SET_ERROR_NOTIFICATIONS] @beneCode, 'Benefit', 'E011', @error
					end
					--Check pending consultation proposals
					else if  exists (select * from APPO_PROPOSALS P
											where
												P.PRST_ID not in (8, 3, 6, 13) --Canceled, Performed, Displayed, Informed
												and P.PPTY_ID in (2, 7) -- Consultation, Periodics
												and P.BENE_ID = @bene_id)
					begin
						set @error = FORMATMESSAGE(N'Has pending consultation proposals (UPDATE-CODE: %s)', @beneCode)
						exec [PROC_SET_ERROR_NOTIFICATIONS] @beneCode, 'Benefit', 'E013', @error
					end
					--Check pending Laboratory or Pathological Anatomy proposals
					else if  exists (select *
												from APPO_PROPOSALS P
													join PROC_PROCEDURES PPR on PPR.APPR_ID = P.APPR_ID
													join PROC_LABORATORIES L on L.PROC_ID = PPR.PROC_ID
													join PROC_LABORATORY_TESTS LT on LT.LABO_ID = L.LABO_ID
													join TEST_TESTS T on T.TEST_ID = LT.TEST_ID
												where
													P.PRST_ID not in (8, 3, 6, 13) --Canceled, Performed, Displayed, Informed
													and P.PPTY_ID in (1, 4) -- Laboratory, Pathological Anatomy
													and T.BENE_ID = @bene_id)
					begin
						set @error = FORMATMESSAGE(N'Has pending Laboratory or Pathological Anatomy proposals (UPDATE-CODE: %s)', @beneCode)
						exec [PROC_SET_ERROR_NOTIFICATIONS] @beneCode, 'Benefit', 'E014', @error
					end
					--Check pending Medical image proposals
					else if  exists (select *
												from APPO_PROPOSALS P
													join PROC_PROCEDURES PPR on PPR.APPR_ID = P.APPR_ID
													join PROC_RAYS R on R.PROC_ID = PPR.PROC_ID
													join PROC_RAY_TESTS RT on RT.PRAY_ID = R.PRAY_ID
													join TEST_TESTS T on T.TEST_ID = RT.TEST_ID
												where
													P.PRST_ID not in (8, 3, 6, 13) --Canceled, Performed, Displayed, Informed
													and P.PPTY_ID =3 -- Medical image
													and T.BENE_ID = @bene_id)
					begin
						set @error = FORMATMESSAGE(N'Has pending Medical image proposals (UPDATE-CODE: %s)', @beneCode)
						exec [PROC_SET_ERROR_NOTIFICATIONS] @beneCode, 'Benefit', 'E015', @error
					end
				end

		if (@action<>1)
		begin
			delete from  PROP_PROP_TYPE_BENEFITS where BENE_ID = @bene_id
		end

		exec [dbo].[PROC_SET_BENE_BENEFITS] @beneCode, @beneDescription, @ppty_ids, @betyCode, @bestCode, @action, @unit, @bene_id OUTPUT

		IF EXISTS (SELECT ID FROM @ppty_ids WHERE ID IN (SELECT ID FROM @proposalWithTest))
		BEGIN
			exec [dbo].[PROC_SET_TEST_TESTS] @beneCode, @beneDescription, @bene_id, @betyCode, @bestCode, @action, @test_id  OUTPUT

			set @isTest=1
		END



	-- Si es una intervención, actualizamos la prestación en el catálogo de procedimientos o de procedimientos de CIE-10

		IF EXISTS (SELECT ID FROM @ppty_ids WHERE ID=10)
		BEGIN
			EXEC [dbo].[PROC_SET_PROCEDURES_BENEFITS]  @bene_id, @beneCode, @action
		END

		if (@action=3)
		begin

		--Reteieve active schedules that have default benefit @bene_id
        -- and delete  default benefit @bene_id  from these schedules
        if exists (select *
					from SCHE_SCHEDULES S
                    join SCHE_SCHEDULE_BENEFITS SC on SC.SCHE_ID = S.SCHE_ID
                    where S.SCHE_ACTIVE = 1 and S.SCHE_DELETED = 0 and SC.BENE_ID = @bene_id)
             begin
               delete SCHE_SCHEDULE_BENEFITS where BENE_ID=@bene_id
             end
        -- If the benefit terminated is the only one existing in a block, the block hours is eliminated
        -- If the template runs out of blocks, the template is disabled .
        -- If the schedule is left without active templates, the schedule is disabled .
        DECLARE @blho_id int, @stem_id int, @sche_id int

		DECLARE @isUpdateBenefitSchedule as bit=0;

		DECLARE @SCHEDULE_TABLE AS TABLE(
			blho_id int
			,stem_id int
			,sche_id int);

		INSERT INTO @SCHEDULE_TABLE (blho_id,stem_id,sche_id)
		(SELECT
                            BHB.BLHO_ID,
                            S.SCHE_Id,
                            T.STEM_ID

                        FROM SCHE_SCHEDULES S
                                 join SCHE_TEMPLATES T on S.SCHE_Id = T.SCHE_ID
                                 join SCHE_BLOCK_HOURS BH on BH.STEM_ID = T.STEM_ID
                                 join SCHE_BLOCK_HOUR_BENEFITS BHB on BHB.BLHO_ID = BH.BLHO_ID
                        where
                                S.SCHE_ACTIVE = 1 and S.SCHE_DELETED = 0
                          and T.STEM_ACTIVE = 1 and T.STEM_DELETED = 0
                          and BH.BLHO_DELETED = 0
                          and BHB.BENE_ID = @bene_id)

		WHILE EXISTS (SELECT TOP 1 * FROM @SCHEDULE_TABLE)
		BEGIN
			SELECT TOP 1 @blho_id=blho_id , @sche_id=sche_id, @stem_id=stem_id FROM @SCHEDULE_TABLE

			set @isUpdateBenefitSchedule=1;

			BEGIN TRY
                DELETE SCHE_BLOCK_HOUR_BENEFITS where BLHO_ID= @blho_id and BENE_ID = @bene_id
				if not exists (select * from  SCHE_BLOCK_HOURS BH join SCHE_BLOCK_HOUR_BENEFITS BHB on BHB.BLHO_ID = BH.BLHO_ID where  BH.BLHO_ID= @blho_id)
                                    begin
                                        update SCHE_BLOCK_HOURS set  BLHO_DELETED = 1,  BLHO_DELETED_DATE = GETDATE() where BLHO_ID= @blho_id
                                        if not exists (select * from SCHE_TEMPLATES T join SCHE_BLOCK_HOURS BH on BH.STEM_ID = T.STEM_ID where T.STEM_ID = @stem_id and  BLHO_DELETED = 0)
                                            begin
                                                update SCHE_TEMPLATES set STEM_ACTIVE = 0 where STEM_ID = @stem_id
                                                if not exists (select * from SCHE_SCHEDULES S join SCHE_TEMPLATES T on S.SCHE_Id = T.SCHE_ID where S.SCHE_Id = @sche_id and T.STEM_ACTIVE = 1  and T.STEM_DELETED = 0)
                                                    begin
                                                        update SCHE_SCHEDULES set SCHE_ACTIVE = 0 where SCHE_Id = @sche_id
                                                    end
                                            end
                                    end
            END TRY
              BEGIN CATCH
                  set @error = FORMATMESSAGE(N'error to delete or disabled  blocks/templates/schedules (DELETE-CODE: %s)', @beneCode)
                  exec [PROC_SET_ERROR_NOTIFICATIONS] @beneCode, 'Benefit', 'E029', @error

				  DELETE TOP (1) FROM @SCHEDULE_TABLE;
              END CATCH


			DELETE TOP (1) FROM @SCHEDULE_TABLE;

		END

		if (@isUpdateBenefitSchedule=1)
		BEGIN
			exec PROC_SET_SCHEDULE_ES @bene_id, 'P'
		END
	END
	COMMIT TRAN T1;
	set @checkUpdate = 1
	END TRY
		BEGIN CATCH
			ROLLBACK TRAN T1;
			set @checkUpdate = 0
			if @error = ''
				set @error = FORMATMESSAGE(N'Benefit error (CODE: %s, ERROR: %s)', @beneCode, ERROR_MESSAGE())
			exec [PROC_SET_ERROR_NOTIFICATIONS] @beneCode, 'Benefit', 'E015', @error, 0
		END CATCH

	if @checkUpdate=1
	BEGIN
		update ERP_Prestacion
			set FLeido = GETDATE()
			where
				[IdPrestacion] = @beneCode
				and FLeido is null
	END

	DELETE TOP (1) FROM @PRESTACIONES
END

exec [dbo].[PROC_SET_BENEFIT_RELATIONS]

END
