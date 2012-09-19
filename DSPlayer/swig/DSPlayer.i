%module DSPlayer
%{
#include "..\DSPlayer.h"
%}

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
	virtual int  OpenFileDialog();

	virtual int  DoPlayOrPause();
	virtual int  DoStop();
	virtual int  DoPlay();
	//int  DoTimerStuff();
	//int  EventReceiver();

private:

	int StartPlayingFile();

	IGraphBuilder *pGraphBuilder;
	IMediaControl *pMediaControl;
	IMediaSeeking *pMediaSeeking;
	IMediaEventEx *pMediaEventEx;

	// keeps track of whether the media is playing or paused/stopped
	bool playing;

	// handle to progress bar
	HWND hProgressBar;


	// total duration of the selected media file
	LONGLONG totalDuration;

	// keeps track of the time elapsed
	long timeElapsed;

	// stores the amount by which to step, used in the progress of the prog bar
	float step;

	// structure that contains info about the file that was opened
	OPENFILENAME priFileInfo;

	// full-path name of the file selected
	wchar_t szFileName[MAX_SIZE];

};

DSPlayer*   CreateDSPlayerObject();

void  DeleteDSPlayerObject(DSPlayer*);

#ifdef __cplusplus
};
#endif

#endif



