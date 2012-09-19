#include "StdAfx.h"
#include "DSPlayer.h"


DSPlayer* __stdcall CreateDSPlayerObject()
{
	return new DSPlayer();
}

void __stdcall DeleteDSPlayerObject(DSPlayer* obj)
{
	delete obj;
	obj = NULL;
}

DSPlayer::DSPlayer(void)
{
	CoInitialize(NULL);

	m_pGraphBuilder		= NULL;
	m_pMediaControl		= NULL;
	m_pMediaSeeking		= NULL;
	m_pMediaEventEx		= NULL;
	m_lltotalDuration		= 0;
	m_ltimeElapsed			= 0;
}


DSPlayer::~DSPlayer(void)
{
	if (m_pGraphBuilder)
	{
		m_pGraphBuilder->Release();
		m_pGraphBuilder = NULL;
	}
	if (m_pMediaControl)
	{
		m_pMediaControl->Release();
		m_pMediaControl = NULL;
	}
	if (m_pMediaSeeking)
	{
		m_pMediaSeeking->Release();
		m_pMediaSeeking = NULL;
	}
	if (m_pMediaEventEx)
	{
		// unset the notify window
		m_pMediaEventEx->SetNotifyWindow(NULL, 0, 0);

		m_pMediaEventEx->Release();
		m_pMediaEventEx = NULL;
	}

	CoUninitialize();
}


HRESULT DSPlayer::Initialize()
{
	HRESULT hr;

	// Get an instance of the graph builder
	CoCreateInstance(CLSID_FilterGraph, NULL, CLSCTX_INPROC_SERVER, IID_IGraphBuilder,
		(void**)&m_pGraphBuilder);

	if (!m_pGraphBuilder)
	{
		MessageBox(NULL, L"Load DLL fail, unable to create graph builder", L"Error", MB_OK);
	}

	// Get the references to interfaces
	hr = m_pGraphBuilder->QueryInterface(IID_IMediaControl, (void **)&m_pMediaControl);
	hr |= m_pGraphBuilder->QueryInterface(IID_IMediaSeeking, (void**)&m_pMediaSeeking);
	hr |= m_pGraphBuilder->QueryInterface(IID_IMediaEventEx, (void**)&m_pMediaEventEx);

	if (!m_pMediaControl || !m_pMediaSeeking || !m_pMediaEventEx)
	{
		MessageBox(NULL, L"Load interface fail.", L"Error", MB_OK);
	}

	m_lltotalDuration = 0;
	m_ltimeElapsed = 0;


	m_bIsPlaying = false;

	return hr;

}

int DSPlayer::OpenFileDialog()
{
	OPENFILENAME ofn;

	ZeroMemory(&ofn, sizeof(ofn));
	ZeroMemory(szFileName, sizeof(szFileName));

	// Initialize 
	ofn.lStructSize = sizeof(ofn);
	ofn.hwndOwner = NULL;
	ofn.lpstrFilter = L"mp3 Files (*.mp3)\0*.mp3\0avi files (*.avi)\0*.avi\0";
	ofn.lpstrFile = szFileName;
	ofn.nMaxFile = MAX_SIZE;
	ofn.Flags = OFN_EXPLORER | OFN_FILEMUSTEXIST | OFN_HIDEREADONLY;
	ofn.lpstrDefExt = L"mp3";

	if (GetOpenFileName(&ofn))
	{
		if (m_bIsPlaying)
			DoStop();
		
		Initialize();
		//memcpy(&priFileInfo, &ofn, sizeof(ofn));
		return 1;
	}

	return 0;
}

int DSPlayer::DoPlay()
{
	return StartPlayingFile();
}

// handle the stop button
int DSPlayer::DoStop()
{
	REFERENCE_TIME rt = 0;

	if (m_pMediaControl != NULL)
	{

		// stop the media if it is playing
		if (m_bIsPlaying)
		{
			m_pMediaControl->Stop();
			m_bIsPlaying = false;
		}

		if (m_pMediaSeeking)
		{
			m_pMediaSeeking->SetPositions(&rt, AM_SEEKING_AbsolutePositioning, NULL, AM_SEEKING_NoPositioning);
		}
		
		m_ltimeElapsed = 0;		
	}

	return 1;

}


int DSPlayer::StartPlayingFile()
{
	WCHAR wFileName[MAX_SIZE];
	char totalTime[MAX_SIZE];
	LONGLONG lDuration100NanoSecs = 0;
	long temporary;

	wcsncpy(wFileName, szFileName, MAX_SIZE);

	// create the filter graph
	m_pGraphBuilder->RenderFile(wFileName, NULL);

	// get the time in units of 100 ns
	m_pMediaSeeking->GetDuration(&lDuration100NanoSecs);

	m_lltotalDuration = lDuration100NanoSecs/10000000;

	// somehow the sprintf (division and mod) doesn't work with LONGLONG so convert this to long
	temporary = (long)m_lltotalDuration;

	// normalizing to 100, see note above
	step = (float)100/temporary;

	// get the total time in printable format (all divs and mods are to get hh:mm:ss
	sprintf(totalTime, "%02u:%02u:%02u", (temporary/3600)%60, (temporary/60)%60, (temporary%60));
	
	m_bIsPlaying = true;

	// play the file
	m_pMediaControl->Run();

	return 1;
}

int DSPlayer::DoPlayOrPause()
{
	if (m_pMediaControl != NULL)
	{
		if (m_bIsPlaying)
		{
			m_pMediaControl->Pause();
			m_bIsPlaying = false;
		}
		else
		{
			m_pMediaControl->Run();
			m_bIsPlaying = true;
		}
	}
	return 1;
}