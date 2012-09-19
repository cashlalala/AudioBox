#pragma once
#ifndef _DS_PLAYER
#define _DS_PLAYER

#ifdef __cplusplus
extern "C"{
#endif

#ifdef _DLL_EXPORT
#define DLL_API __declspec(dllexport)
#else
#define DLL_API __declspec(dllimport)
#endif

#include "stdafx.h"
#include <DShow.h>
#include <CommDlg.h>

#define MAX_SIZE 256

class DSPlayer
{

public:
	DSPlayer();
	~DSPlayer();

	// does some initialization of the member variables
	HRESULT Initialize();

	// opens the file dialog and lets the user select a file
	virtual int __stdcall OpenFileDialog();

	virtual int __stdcall DoPlayOrPause();
	virtual int __stdcall DoStop();
	virtual int __stdcall DoPlay();
	//int __stdcall DoTimerStuff();
	//int __stdcall EventReceiver();

private:

	int StartPlayingFile();

	IGraphBuilder *m_pGraphBuilder;
	IMediaControl *m_pMediaControl;
	IMediaSeeking *m_pMediaSeeking;
	IMediaEventEx *m_pMediaEventEx;

	// keeps track of whether the media is playing or paused/stopped
	bool m_bIsPlaying;
	
	// total duration of the selected media file
	LONGLONG m_lltotalDuration;

	// keeps track of the time elapsed
	long m_ltimeElapsed;

	// stores the amount by which to step, used in the progress of the prog bar
	float step;

	// structure that contains info about the file that was opened
	OPENFILENAME priFileInfo;

	// full-path name of the file selected
	wchar_t szFileName[MAX_SIZE];

};

DLL_API DSPlayer* __stdcall  CreateDSPlayerObject();

DLL_API void __stdcall DeleteDSPlayerObject(DSPlayer*);

#ifdef __cplusplus
};
#endif

#endif



