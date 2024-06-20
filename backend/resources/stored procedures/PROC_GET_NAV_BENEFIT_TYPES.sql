USE [sinasuite]
SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;

BEGIN

Declare @betyCode as nvarchar(50)=''								-- C?digo de familia	(tipo de prestaci?)
Declare @betyDescription as nvarchar(300)	=''			-- Descripci?n de la familia
Declare @bestCode as nvarchar(50)	=''					-- C?digo de subfamilia (subtipo de prestaci?)
Declare @bestDescription as nvarchar(300) =''		-- Descripci?n de la subfamilia
Declare @active as bit														-- Flag de activo
Declare @checkUpdate as bit = 0;
Declare @error as nvarchar(2000) = ''
Declare @ppty_ids as SINA_List;
Declare @okBenefitType as bit = 0;
Declare @okTestType as bit = 0;
Declare @best_ids as SINA_List
Declare @proposalWithTest as SINA_List;

-- Tabla para guardar los tipos de propuestas que requieren de test en sina.
INSERT INTO @proposalWithTest (id) SELECT PPTY_ID FROM PROP_PROPOSAL_TYPES WHERE PPTY_REQUIRED_TEST=1

--Tabla para leer los registros aprocesar
-- Se leen los registros no procesados (FLeido is null)

DECLARE @FAMILIA_TIPO_PETICION AS TABLE (
	betyCode NVARCHAR(50)
	,betyDescription NVARCHAR(300)
	,activo Sina_flag
	,pptyIds NVARCHAR(250)
	);

-- Insertamos en la tabla temporal con la que vamos a trabajar.
--La última columna en una lista de los tipos de petición asociados al tipo de prestación.
	insert into @FAMILIA_TIPO_PETICION (betyCode,betyDescription,activo,pptyIds)
	 (SELECT  [IdFamilia]				-- C?digo de familia	(tipo de prestaci?n)
		  ,ef.[Descripcion] as descripcion		-- Descripci?n de la familia
		  ,[Activo]					-- Flag de activo
		  ,(SELECT TOP 1 CONCAT(STUFF(
				(SELECT ','+CONVERT(VARCHAR(10),ProposalTypeId) AS [text()]
					FROM erp_tipoprestacion tp
					WHERE tp.proposaltypeId is not null and tp.codigo = ef.codtipo
					FOR XML PATH('')), 1, 1, ''),'')
				FROM erp_tipoprestacion T) as proposalTypesList
				 				-- C?digo de tipo de prestaci?n (Indica el tipo de solicitud a aplicar la prestaci?n)
	  FROM ERP_Familia ef

	  where
		 FLeido is null AND EF.CODTIPO IN (SELECT CODIGO FROM ERP_TIPOPRESTACION) AND IDFAMILIA IS NOT NULL AND EF.DESCRIPCION IS NOT NULL
		 )

-- Comenzamos a recorrer la tabla temporal
	WHILE EXISTS (SELECT TOP 1 * FROM @FAMILIA_TIPO_PETICION)
	BEGIN
		BEGIN TRY
		-- Iniciamos una transacción por si hubiera que ejecutar un rollback
			BEGIN TRAN T1

			Declare @ppty_ids_string NVARCHAR(250);
			-- Esta será la acción que estamos realizando: 1 Creación, 2 Modificación 3 eliminación.
			Declare @action int;
			-- Por cada tipo de prestación inicializamos el array de tipos de solucitudes asociadas. Esto es porque el campo en la tabla temporal es un String y ahora nos interesa un list.
			DELETE from @ppty_ids;

			SELECT TOP 1 @active=activo,@ppty_ids_string=pptyIds,@betyCode=betyCode,@betyDescription=betyDescription
				FROM @FAMILIA_TIPO_PETICION;

			INSERT INTO @ppty_ids (id) (SELECT id FROM [dbo].SplitString(@ppty_ids_string, ','))
			set @okTestType=1;

			IF (@active = 1 or @active is null)
			BEGIN

		--Si no existe un registro previo del tipo de prestación será una creación, sino será una modificación.
				IF NOT EXISTS (SELECT DISTINCT BETY_ID FROM ORMA_BENEFIT_TYPES WHERE BETY_CODE=@betyCode)
				BEGIN
					set @action=1;
				END
				ELSE
				BEGIN
					set @action=2;
				END

			END
			ELSE
			-- Si nos están enviado un active a false quiere decir que están borrando el tipo de prestación, por lo que habrá que hacer una serie de validaciones antes de borrar
			BEGIN
				---------------------------------
				-- Checks
				---------------------------------
				--Check Family has active benefits
				if exists (select b.BENE_ID from  ORMA_BENEFITS b where	b.BETY_ID in (SELECT DISTINCT BETY_ID FROM ORMA_BENEFIT_TYPES WHERE BETY_CODE=@betyCode AND BETY_DELETED=0) AND BENE_DELETED=0)
					begin
						set @error = FORMATMESSAGE(N'Family has active benefits (CODE: %s - %s)', @betyCode, @betyDescription)
						exec [PROC_SET_ERROR_NOTIFICATIONS] @betyCode, 'BenefitType', 'E016', @error
					end
					--Check SubFamily has active benefits
					else if exists (select BST.BEST_ID	from  ORMA_BENEFIT_SUBTYPES  BST where BST.BEST_DELETED = 0  and BST.BETY_ID in (SELECT DISTINCT BETY_ID FROM ORMA_BENEFIT_TYPES WHERE BETY_CODE=@betyCode AND BETY_DELETED=0))
						begin
							set @error = FORMATMESSAGE(N'Family has active subfamilies (CODE: %s - %s)', @betyCode, @betyDescription)
							exec [PROC_SET_ERROR_NOTIFICATIONS] @betyCode, 'BenefitType', 'E017', @error
						end
						else
							begin
							 set @action=3;
							end
			END

			-- Por último llamamos al PA de cargar de tipos de prestación y que asocia dichos tipos a los tipos de petición.
			exec [dbo].[PROC_SET_BENE_BENEFIT_TYPES] @ppty_ids, @betyCode, @betyDescription, @action, @okBenefitType OUTPUT
			-- Si alguno de los tipos de petición requiere de pruebas, creamos la entrada de tipos de test.
				IF EXISTS (SELECT ID FROM @ppty_ids WHERE ID IN (SELECT ID FROM @proposalWithTest))
				BEGIN
					exec [dbo].[PROC_SET_TEST_TEST_TYPES] @ppty_ids, @betyCode, @betyDescription, @action, @okTestType OUTPUT
				END
				-- Si algo no ha ido bien, guardamos el error.
				if @okBenefitType <> 1
				begin
					set @error = FORMATMESSAGE(N'Benefit type no created (CREATE-CODE: %s - %s)', @betyCode, @betyDescription)
					exec [PROC_SET_ERROR_NOTIFICATIONS] @betyCode, 'BenefitType', 'E020', @error, 0
				end
				else if (@okTestType <> 1)
					begin
						set @error = FORMATMESSAGE(N'Test type no created (CREATE-CODE: %s - %s)', @betyCode, @betyDescription)
						exec [PROC_SET_ERROR_NOTIFICATIONS] @betyCode, 'BenefitType', 'E027', @error, 0
					end
				print(N'ACCION: (' + CAST(@action as varchar(1)) + '): (' +  @betyCode + ' - ' + @betyDescription +') ' )
	COMMIT TRAN T1;
	set @checkUpdate = 1

	END TRY
	BEGIN CATCH
	--En caso de error ejecuta el rollback.
				ROLLBACK TRAN T1;
				set @checkUpdate = 0;
				if @error = ''
					set @error = FORMATMESSAGE(N'BenefitType error (CODE: %s, ERROR: %s)', @betyCode, ERROR_MESSAGE())

				exec [PROC_SET_ERROR_NOTIFICATIONS] @betyCode, 'BenefitType', 'E019', @error, 0

	END CATCH
	--Marcamos el registro en la tabla intermedia como leido.
	if @checkUpdate=1
			update ERP_Familia
				set FLeido = GETDATE()
				where [IdFamilia] = @betyCode and FLeido is null
	--Eliminamos el registro con el que acabamos de trabajar y continuamos con el siguiente.
	DELETE TOP (1) FROM @FAMILIA_TIPO_PETICION;
END

--Ahora cargamos las subfamilias
DECLARE @SUBFAMILIA AS TABLE (
	betyCode NVARCHAR(50)
	,bestCode NVARCHAR(50)
	,bestDescription NVARCHAR(300)
	,activo Sina_flag
	,isTest Sina_flag
	);

DECLARE @isTest Sina_flag;

insert into @SUBFAMILIA (betyCode,bestCode,bestDescription,activo,isTest)
	 (SELECT  [IdFamilia]			-- C?digo de familia	(tipo de prestaci?n)
	 ,[IdSubFamilia]				-- C?digo de subfamilia	(tipo de prestaci?n)
	 ,ef.[Descripcion] as descripcion		-- Descripci?n de la familia
	 ,[Activo]					-- Flag de activo
	 ,CASE WHEN EXISTS (select top 1 ppbty.BETY_ID
		from PROP_PROP_TYPE_BENEFIT_TYPES PPBTY
		INNER JOIN ORMA_BENEFIT_TYPES OBT ON OBT.BETY_ID=PPBTY.BETY_ID AND OBT.BETY_CODE=ef.IdFamilia COLLATE Modern_Spanish_CI_AS
		WHERE PPBTY.PPTY_ID IN (select id from @proposalWithTest))
		THEN 1
		ELSE 0
	 END AS isTests

	  FROM ERP_SubFamilia ef

	  where
		 FLeido is null
		)


WHILE EXISTS (SELECT TOP 1 * FROM @SUBFAMILIA)
	BEGIN
		BEGIN TRY
		-- Iniciamos una transacción por si hubiera que ejecutar un rollback
			BEGIN TRAN T2

				SELECT TOP 1 @betyCode=betyCode,@bestCode=bestCode,@bestDescription=bestDescription,@active=activo,@isTest=isTest
				FROM @SUBFAMILIA;

			set @okTestType=1;

			IF (@active = 1 or @active is null)
			BEGIN

		--Si no existe un registro previo del subtipo de prestación será una creación, sino será una modificación.
				IF NOT EXISTS (SELECT DISTINCT BEST_ID FROM ORMA_BENEFIT_SUBTYPES WHERE BEST_CODE=@bestCode)
				BEGIN
					set @action=1;
				END
				ELSE
				BEGIN
					set @action=2;
				END

			END
			ELSE
			-- Si nos están enviado un active a false quiere decir que están borrando el subtipo de prestación, por lo que habrá que hacer una serie de validaciones antes de borrar
			BEGIN
				---------------------------------
				-- Checks
				---------------------------------
				--Check si la subfamilia tiene prestaciones asociadas.
				if exists (select b.BEST_ID from  ORMA_BENEFITS b where	b.BEST_ID in (SELECT DISTINCT BEST_ID FROM ORMA_BENEFIT_SUBTYPES WHERE BEST_CODE=@bestCode AND BEST_DELETED=0) AND BENE_DELETED=0)
					begin
						set @error = FORMATMESSAGE(N'Benefit subtype has active benefits (CODE: %s - %s)', @bestCode, @bestDescription)
						exec [PROC_SET_ERROR_NOTIFICATIONS] @bestCode, 'BenefitSubType', 'E018', @error
					end
					--Check SubFamily has active benefits
					else
						begin
						 set @action=3;
						end
			END
			exec [PROC_SET_BENE_BENEFIT_SUBTYPES] @betyCode, @bestCode, @bestDescription, @action, @okBenefitType OUTPUT;

			if @isTest = 1
				exec [PROC_SET_TEST_TEST_SUBTYPES] @betyCode, @bestCode, @bestDescription, @action, @okTestType OUTPUT

		COMMIT TRAN T2;
		set @checkUpdate = 1
		END TRY
			BEGIN CATCH
				ROLLBACK TRAN T2;
				set @checkUpdate = 0
				if @error = ''
					set @error = FORMATMESSAGE(N'Benefit subtype error (CODE: %s, ERROR: %s)', @bestCode, ERROR_MESSAGE())
				exec [PROC_SET_ERROR_NOTIFICATIONS] @bestCode, 'BenefitSubType', 'E022', @error, 0
			END CATCH

		if @checkUpdate=1
			update ERP_SubFamilia
				set
					FLeido = GETDATE()
				where
					[IdFamilia] = @betyCode
					and [IdSubFamilia] = @bestCode
					and FLeido is null

		--Eliminamos el registro con el que acabamos de trabajar y continuamos con el siguiente.
		DELETE TOP (1) FROM @SUBFAMILIA;
END
END

