// dllmain.cpp : Defines the entry point for the DLL application.
#include "stdafx.h"
#include <stdio.h>

BOOL APIENTRY DllMain( HMODULE hModule,
					   DWORD  ul_reason_for_call,
					   LPVOID lpReserved
					 )
{
	switch (ul_reason_for_call)
	{
	case DLL_PROCESS_ATTACH:
		wprintf_s(L"process attached>>>>>>>>>>>>>>>>>>>>\n");
		break;
	case DLL_THREAD_ATTACH:
		wprintf_s(L"thread attached>>>>>>>>>>>>>>>>>>>>\n");
		break;
	case DLL_THREAD_DETACH:
		wprintf_s(L"thread detached>>>>>>>>>>>>>>>>>>>>\n");
		break;
	case DLL_PROCESS_DETACH:
		wprintf_s(L"process detached>>>>>>>>>>>>>>>>>>>>\n");
		break;
	}
	return TRUE;
}

