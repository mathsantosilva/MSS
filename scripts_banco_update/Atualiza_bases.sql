USE [DataBaseNewPoint]
GO

--VERSAO 001

--Criação da tebela kairos_databases
IF NOT EXISTS (SELECT name FROM sysobjects WHERE name = 'KAIROS_DATABASES' AND type='U')
BEGIN
	SET ANSI_NULLS ON

	SET QUOTED_IDENTIFIER ON

	CREATE TABLE [dbo].[kairos_databases](
		[DATABASE_ID] [int] IDENTITY(1,1) NOT NULL,
		[CONNECTION_STRING] [varchar](200) NOT NULL,
		[DATABASE_VERSION] [int] NOT NULL,
		[FL_MAQUINA_CALCULO] [bit] NOT NULL,
		[FL_ATIVO] [bit] NOT NULL,
	 CONSTRAINT [PK_KAIROS_DATABASES] PRIMARY KEY CLUSTERED 
	(
		[DATABASE_ID] ASC
	)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, FILLFACTOR = 90, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
	) ON [PRIMARY]

	ALTER TABLE [dbo].[KAIROS_DATABASES] ADD  DEFAULT ((0)) FOR [FL_MAQUINA_CALCULO]

	ALTER TABLE [dbo].[KAIROS_DATABASES] ADD  CONSTRAINT [DF_FL_ATIVO]  DEFAULT ('1') FOR [FL_ATIVO]
END
GO

--Criação da tebela historicos
IF NOT EXISTS (SELECT name FROM sysobjects WHERE name = 'historicos' AND type='U')
BEGIN
	SET ANSI_NULLS ON

	SET QUOTED_IDENTIFIER ON

	CREATE TABLE [dbo].[historicos](
		[id] [int] IDENTITY(1,1) NOT NULL,
		[version] [nchar](10) NULL,
		[qtda_registros] [nvarchar](50) NULL,
		[data] [datetime] NULL
	) ON [PRIMARY]
END
GO

--Criação da tebela versions
IF NOT EXISTS (SELECT name FROM sysobjects WHERE name = 'versions' AND type='U')
BEGIN
	SET ANSI_NULLS ON

	SET QUOTED_IDENTIFIER ON

	CREATE TABLE [dbo].[versions](
		[id] [int] IDENTITY(1,1) NOT NULL,
		[descricao_atualizacao] [nvarchar](50) NULL,
		[version] [nchar](10) NULL,
		[date] [datetime] NULL
	) ON [PRIMARY]
END
GO


-- Inserindo o version da atualização do banco 001
IF NOT EXISTS (SELECT [version] FROM [DataBaseNewPoint].[dbo].[versions] WHERE [version] = 001 )
BEGIN
	INSERT INTO [DataBaseNewPoint].[dbo].[versions] ([descricao_atualizacao], [version], [date]) VALUES ('Criando as tabelas historicos e versions',001, GETDATE())
END
GO