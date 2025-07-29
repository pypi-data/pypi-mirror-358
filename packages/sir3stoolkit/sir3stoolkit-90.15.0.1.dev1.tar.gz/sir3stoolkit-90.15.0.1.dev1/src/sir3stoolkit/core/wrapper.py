
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 14:46:49 2024

@author: Giriyan
"""

#**********************************************************************************
# IMPORTANT NOTICE FOR USER MANUAL (2024-12-06 NTC): 
# The Meaning and Limitations of all Method-Parameters
# are literally written in the Definition of the Interface 'ISir3SToolkitModel'.
# So it may be helpful to copy/paste them when writing the User Manual.
#
# AFTER SEVERAL ATTEMPTS (maybe 26), VISUAL STUDIO FORCED ME (NTC) TO USE Python3.9
#**********************************************************************************

import sys
from turtle import fillcolor
import clr as net
import random
import inspect
import os
import System
from collections import namedtuple
import numpy as np

# Global variables
SIR3S_SIRGRAF_DIR = None

# User defined types
textProperties = namedtuple("textProperties", ["x", "y", "color", "textContent", "angle_degree", "faceName", 
                                       "heightPt", "isBold", "isItalic", "isUnderline", "idRef", "description"])

numericalDisplayProperties = namedtuple("numericalDisplayProperties", ["x", "y", "color", "angle_degree", "faceName", 
                                                                       "heightPt", "isBold", "isItalic", "isUnderline",
                                                                       "description", "forResult", "tkObserved", "elemPropertyNameOrResult", 
                                                                       "prefix", "unit", "numDec", "absValue"])

fontInformation = namedtuple("fontInformation", ["textContent", "color", "angle_degree", "faceName", 
                                       "heightPt", "isBold", "isItalic", "isUnderline"])


# CAUTION: User should call this function before creating any instances of the classes provoded through this library !!!
#          Failed to do so will result in incorrect initialization of classes and object model that are key components to
#          interact with Sir3S

# Function to initialize the toolkit with correct SirGraf path
def Initialize_Toolkit(basePath: str):
    global SIR3S_SIRGRAF_DIR
    
    if ((basePath is None) or (basePath is System.String.Empty)):
        print("SirGraf directory is Empty or None")

    else:
        SIR3S_SIRGRAF_DIR = basePath
        sys.path.append(SIR3S_SIRGRAF_DIR)
   
        net.AddReference(r"System")
                
        net.AddReference(SIR3S_SIRGRAF_DIR+r"\Sir3S_Repository.ModelManager")  
        net.AddReference(SIR3S_SIRGRAF_DIR+r"\Sir3S_Repository.Utilities")
        net.AddReference(SIR3S_SIRGRAF_DIR+r"\Sir3S_Repository.Interfaces")
        
        # THE COMPILED DLL FOR Sir3S_Toolkit SHOULD ALSO BE COPIED TO SIR3S_SIRGRAF_DIR
        net.AddReference(SIR3S_SIRGRAF_DIR+r"\Sir3S_Toolkit")


"""
Class definition of SIR3S_Model() wrapper to access functionalities provided by SIR3S software
This can be used independently or by using inside python console plugin to give better control over the model for users
"""

class SIR3S_Model:
    def __init__(self):
        # Basic imports to dlls provided by SirGraf
        # This will only work if Initialize_Toolkit() is called in the same context
        import Sir3S_Repository.ModelManager
        import Sir3S_Repository.Utilities as Util
        import Sir3S_Repository.Interfaces as Interfaces
        import Sir3S_Toolkit.Model as Sir3SToolkit
        
        # Create the toolkit
        self.toolkit = Util.StaticUI.Toolkit
        if self.toolkit == None:
            self.toolkit = Sir3SToolkit.CSir3SToolkitFactory.CreateToolkit(None, SIR3S_SIRGRAF_DIR, r"90-15-00-01")
        if (self.toolkit is None):
            print("Error in initializing the toolkit")
        else:
            print("Initialization complete")
        
    def StartTransaction(self, SessionName: str):
        """
        Start a transaction with the given session name.

        :param SessionName: A meaningful name to start a transaction; Empty string or None will lead to error.
        :type SessionName: str
        :return: None
        :rtype: None
        :description: This method is a wrapper method for StartTransaction() from toolkit.
        """
        isTransactionStarted, message = self.toolkit.StartTransaction(SessionName)
        if not isTransactionStarted:
            print(message)
        else:
            if message == "":
                print("Now you can make changes to the model")
            else:
                print(message)

    def EndTransaction(self):
        """
        End the current transaction.

        :return: None
        :rtype: None
        :description: This method is a wrapper method for EndTransaction() from toolkit. Use it after StartTransaction() to close that transaction.
        """
        isTransactionEnded, message = self.toolkit.EndTransaction()
        if not isTransactionEnded:
            print(message)
        else:
            if message == "":
                print("Transaction has ended. Please open up a new transaction if you want to make further changes")
            else:
                print(message)
          
    def StartEditSession(self, SessionName: str):
        """
        Start an edit session with the given session name.

        :param SessionName: A meaningful name to start a session.
        :type SessionName: str
        :return: None
        :rtype: None
        :description: This method is a wrapper method for StartEditSession() from toolkit.
        """
        isTransactionStarted, message = self.toolkit.StartEditSession(SessionName)
        if not isTransactionStarted:
            print(message)
        else:
            if message == "":
                print("Now you can make changes to the model")
            else:
                print(message)
            
    def EndEditSession(self):
        """
        End the current edit session.

        :return: None
        :rtype: None
        :description: This method is a wrapper method for EndEditSession() from toolkit. Use it after StartEditSession() to close that session.
        """
        isTransactionEnded, message = self.toolkit.EndEditSession()
        if not isTransactionEnded:
            print(message)
        else:
            if message == "":
                print("Edit Session has ended. Please open up a new session if you want to make further changes")
            else:
                print(message)

    def GetCurrentTimeStamp(self) -> str:
        """
        Returns the value of the current time stamp.

        :return: Current time stamp.
        :rtype: str
        :description: This is a wrapper method to access the get method for the property CurrentTimestamp from toolkit.
        """
        return self.toolkit.CurrentTimestamp
    
    def SetCurrentTimeStamp(self, timestamp: str):
        """
        Sets the current time stamp.

        :param timestamp: Time stamp value to be set.
        :type timestamp: str
        :return: None
        :rtype: None
        :description: This is a wrapper method to access the set method for the property CurrentTimestamp from toolkit.
        """
        self.toolkit.CurrentTimestamp = timestamp

    def GetValue(self, Tk: str, propertyName: str) -> tuple[str, str]:
        """
        Gets the value for the given element's property.

        :param Tk: The pk/tk of the element in question.
        :type Tk: str
        :param propertyName: Property of the element for which you want the value.
        :type propertyName: str
        :return: Value and type of the value returned.
        :rtype: tuple[str, str]
        :description: This is a wrapper method for GetValue() from toolkit; Watch out for error message for more information.
        """
        value, isFound, valueType, error = self.toolkit.GetValue(Tk, propertyName)
        if value is None:
            print(f"Error: {error}")
        return value, valueType
    
    def SetValue(self, Tk: str, propertyName: str, Value: str):
        """
        Sets the value for the given element's property.

        :param Tk: The pk/tk of the element in question.
        :type Tk: str
        :param propertyName: Property of the element for which you want to set the value.
        :type propertyName: str
        :param Value: Value to be set.
        :type Value: str
        :return: None
        :rtype: None
        :description: This is a wrapper method for SetValue() from toolkit; Watch out for error message for more information.
        """
        isValueSet, error = self.toolkit.SetValue(Tk, propertyName, Value)
        if(isValueSet):
            print("Value is set")
        else:
            print(f"Error: {error}")
        
    def OpenModelXml(self, Path: str, SaveCurrentModel: bool):
        """
        Opens a model from an XML file.

        :param Path: Path to XML file.
        :type Path: str
        :param SaveCurrentModel: Do you want to save the current model before closing it?
        :type SaveCurrentModel: bool
        :return: None
        :rtype: None
        :description: This is a wrapper method for OpenModelXml() from toolkit; Watch out for error message for more information.
        """
        result, error = self.toolkit.OpenModelXml(Path, SaveCurrentModel)
        if(result == True):
            print("Model is open for further operation")
        else:
            print("Error while opening the model," + error)

    def OpenModel(self, dbName: str, providerType, Mid: str, saveCurrentlyOpenModel: bool, namedInstance: str, userID: str, password: str):
        """
        Opens a model from a database file.

        :param dbName: Full path to the database file.
        :type dbName: str
        :param providerType: Provider type from the enum.
        :type providerType: Interfaces.SirDBProviderType
        :param Mid: Model identifier.
        :type Mid: str
        :param saveCurrentlyOpenModel: Do you want to save the current model before closing it?
        :type saveCurrentlyOpenModel: bool
        :param namedInstance: Instance name of the SQL Server.
        :type namedInstance: str
        :param userID: User ID for authentication, only needed for ORACLE and for SQLServer only if SQLServer authentication is required.
        :type userID: str
        :param password: Password for authentication, only needed for ORACLE and for SQLServer only if SQLServer authentication is required.
        :type password: str
        :return: None
        :rtype: None
        :description: This is a wrapper method for OpenModel() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.OpenModel(dbName, providerType, Mid, saveCurrentlyOpenModel, namedInstance, userID, password)
        if(result == True):
            print("Model is open for further operation")
        else:
            print("Error while opening the model, " + error)

    def ExecCalculation(self, waitForSirCalcToExit: bool):
        """
        Executes the model calculation.

        :param waitForSirCalcToExit: Do you want to wait for SirCalc engine to exit before proceeding?
        :type waitForSirCalcToExit: bool
        :return: None
        :rtype: None
        :description: This is a wrapper method for ExecCalculation() from toolkit; Watch out for errors for more information.
        """
        isExecuted, error = self.toolkit.ExecCalculation(waitForSirCalcToExit)
        if not isExecuted:
            print(f"Could not start Model Calculation: {error}")
        else:
            print("Model Calculation is complete")

    def GetTimeStamps(self) -> tuple[list, str, str, str]:
        """
        Gets all available timestamps as ISO formatted strings.

        :return: Array with all available timestamps as ISO formatted strings.
        :rtype: tuple[list, str, str, str]
        :description: This is a wrapper method for GetTimeStamps() from toolkit; Watch out for errors for more information.
        """
        timestamps, error, tsStat, tsMin, tsMax = self.toolkit.GetTimeStamps()
        if len(timestamps) == 0:
            print(f"Error : {error}")
        return list(timestamps), tsStat, tsMin, tsMax

    def GetTksofElementType(self, ElementType) -> list:
        """
        Gets all Tk's belonging to the elements of the specified type.

        :param ElementType: Object type defined in the enum.
        :type ElementType: Interfaces.Sir3SObjectTypes
        :return: List of all Tk's belonging to the elements of type 'ElementType'.
        :rtype: list
        :description: This is a wrapper method for GetAllElementKeys() from toolkit.
        """
        Tk_list = None
        Tk_list = self.toolkit.GetAllElementKeys(ElementType)
        if list(Tk_list) is None:
            print(f"Couldn't retrieve any Tk of element type {ElementType}") 
        return list(Tk_list)

    def GetNetworkType(self):
        """
        Gets the network type.

        :return: Network type defined in the enum.
        :rtype: Interfaces.NetworkType
        :description: This is a wrapper method for GetNetworkType() from toolkit.
        """
        return self.toolkit.GetNetworkType()

    def IsMainContainer(self, fkCont: str) -> bool:
        """
        Tests if the provided Key (TK) is the Key of the main container of the model.

        :param fkCont: Tk of the object in question.
        :type fkCont: str
        :return: Boolean value indicating if it is the main container.
        :rtype: bool
        :description: This is a wrapper method for IsMainContainer() from toolkit.
        """
        return self.toolkit.IsMainContainer(fkCont)

    def GetMainContainer(self):
        """
        Finds the main container of the model and returns its Key (TK).

        :return: Tk of the main container and object type.
        :rtype: tuple[str, Interfaces.Sir3SObjectTypes]
        :description: This is a wrapper method for GetMainContainer() from toolkit.
        """
        Tk, objType, error = self.toolkit.GetMainContainer()
        if Tk == "-1":
            print("Error: " + error)
        return Tk, objType
    def GetElementInfo(self, Tk: str):
        """
        Gets the element information.

        :param Tk: The pk/tk of the element in question.
        :type Tk: str
        :return: None
        :rtype: None
        :description: This is a wrapper method for GetElementInfo() from toolkit; Watch out for errors for more information.
        """
        info, error = self.toolkit.GetElementInfo(Tk)
        if info == "":
            print(f"Error is : {error}")
        else:
            print(f"Info: {info}")

    def GetNumberOfElements(self, ElementType) -> int:
        """
        Gets the total number of elements of the specified type.

        :param ElementType: Object type defined in the enum.
        :type ElementType: Interfaces.Sir3SObjectTypes
        :return: Total number of elements of type 'ElementType'.
        :rtype: int
        :description: This is a wrapper method for GetNumberOfElements() from toolkit.
        """
        return self.toolkit.GetNumberOfElements(ElementType)

    def GetPropertiesofElementType(self, ElementType) -> list:
        """
        Gets all properties belonging to the element of the specified type.

        :param ElementType: Object type defined in the enum.
        :type ElementType: Interfaces.Sir3SObjectTypes
        :return: List of all properties belonging to the element of type 'ElementType'.
        :rtype: list
        :description: This is a wrapper method for GetPropertyNames() from toolkit.
        """
        Properties_list = None
        Properties_list = self.toolkit.GetPropertyNames(ElementType)
        if list(Properties_list) is None:
            print(f"Couldn't retrieve any Properties for the element type {ElementType}")
        return list(Properties_list)

    def GetObjectTypeof_Key(self, Key: str):
        """
        Gets the type of object the input Key belongs to.

        :param Key: The pk/tk of the element in question.
        :type Key: str
        :return: Type of object the input Key belongs to.
        :rtype: Interfaces.Sir3SObjectTypes
        :description: This is a wrapper method for GetObjectTypeOf_Key() from toolkit; Watch out for errors for more information.
        """
        objectType = self.toolkit.GetObjectTypeOf_Key(Key)
        return objectType

    def DeleteElement(self, Tk: str):
        """
        Deletes the specified element.

        :param Tk: The pk/tk of the element to be deleted.
        :type Tk: str
        :return: None
        :rtype: None
        :description: This is a wrapper method for DeleteElement() from toolkit; Watch out for errors for more information.
        """
        isDeleted, info, error = self.toolkit.DeleteElement(Tk)
        if not isDeleted:
            print(f"Error: {error}")
        else:
            print("Element deleted successfully")

    def InsertElement(self, ElementType, IdRef: str) -> str:
        """
        Inserts a new element of the specified type.

        :param ElementType: Object type defined in the enum to be inserted.
        :type ElementType: Interfaces.Sir3SObjectTypes
        :param IdRef: Id reference.
        :type IdRef: str
        :return: Tk of the element inserted.
        :rtype: str
        :description: This is a wrapper method for InsertElement() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.InsertElement(ElementType, IdRef)
        if result == "-1":
            print(f"Error : {error}")
        else:
            print(f"Element inserted successfully into the model with Tk: {result}")
        return result

    def NewModel(self, dbName: str, providerType, netType, modelDescription: str, namedInstance: str, userID: str, password: str):
        """
        Creates a new model.

        :param dbName: Full path to the database file.
        :type dbName: str
        :param providerType: Provider type from the enum.
        :type providerType: Interfaces.SirDBProviderType
        :param netType: Network type.
        :type netType: Interfaces.NetworkType
        :param modelDescription: Description of the model to be created.
        :type modelDescription: str
        :param namedInstance: Instance name of the SQL Server.
        :type namedInstance: str
        :param userID: User ID for authentication, only needed for ORACLE and for SQLServer only if SQLServer authentication is required.
        :type userID: str
        :param password: Password for authentication, only needed for ORACLE and for SQLServer only if SQLServer authentication is required.
        :type password: str
        :return: None
        :rtype: None
        :description: This is a wrapper method for NewModel() from toolkit; Watch out for errors for more information.
        """
        modelIdentifier, error = self.toolkit.NewModel(dbName, providerType, netType, modelDescription, namedInstance, userID, password)
        if modelIdentifier == "-1":
            print(f"Error : {error}")
        else:
            print(f"New model is created with the model identifier: {modelIdentifier}")

    def ConnectConnectingElementWithNodes(self, Tk: str, keyOfNodeI: str, keyOfNodeK: str):
        """
        Connects the specified connecting element with nodes.

        :param Tk: Tk of the connecting object.
        :type Tk: str
        :param keyOfNodeI: Tk of node I (one of the elements that needs to be connected).
        :type keyOfNodeI: str
        :param keyOfNodeK: Tk of node K (other element that needs to be connected).
        :type keyOfNodeK: str
        :return: None
        :rtype: None
        :description: This is a wrapper method for ConnectConnectingElementWithNodes() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.ConnectConnectingElementWithNodes(Tk, keyOfNodeI, keyOfNodeK)
        if not result:
            print("Error: " + error)
        else:
            print("Objects connected successfully")

    def ConnectBypassElementWithNode(self, Tk: str, keyOfNodeI: str):
        """
        Connects the specified bypass element with a node.

        :param Tk: Tk of the connecting object.
        :type Tk: str
        :param keyOfNodeI: Tk of node I (element that needs to be connected).
        :type keyOfNodeI: str
        :return: None
        :rtype: None
        :description: This is a wrapper method for ConnectBypassElementWithNode() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.ConnectBypassElementWithNode(Tk, keyOfNodeI)
        if not result:
            print("Error: " + error)
        else:
            print("Object connected successfully")

    def SaveChanges(self):
        """
        Saves changes made to the model.

        :return: None
        :rtype: None
        :description: This is a wrapper method for SaveChanges() from toolkit; Use it after End{EditSession/Transaction}. Watch out for errors for more information.
        """
        isSaved, error = self.toolkit.SaveChanges()
        if not isSaved:
            print(f"Error: {error}")
        else:
            print("Changes saved successfully")

    def AddTableRow(self, tablePkTk: str):
        """
        Adds a row to the specified table.

        :param tablePkTk: Key of the table.
        :type tablePkTk: str
        :return: Tk of the inserted row and object type.
        :rtype: tuple[str, Interfaces.SirDBProviderType]
        :description: This is a wrapper method for AddTableRow() from toolkit; Watch out for errors for more information.
        """
        Tk, objectType, error = self.toolkit.AddTableRow(tablePkTk)
        if Tk == "-1":
            print("Error: " + error)
        else:
            print(f"Row is added to the table with Tk: {Tk}")
        return Tk, objectType

    def GetTableRows(self, tablePkTk: str):
        """
        Gets all rows of the specified table.

        :param tablePkTk: Key of the table.
        :type tablePkTk: str
        :return: List of Tk's of all rows of the table and object type.
        :rtype: tuple[list, Interfaces.SirDBProviderType]
        :description: This is a wrapper method for GetTableRows() from toolkit; Watch out for errors for more information.
        """
        Tk_list, objectType, error = self.toolkit.GetTableRows(tablePkTk)
        if Tk_list is None:
            print("Error: " + error)
        return Tk_list, objectType

    def RefreshViews(self):
        """
        Refreshes the views.

        :return: None
        :rtype: None
        :description: This is a wrapper method for RefreshViews() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.RefreshViews()
        if not result:
            print("Error: " + error)
        else:
            print("Refresh successful")

    def SetInsertPoint(self, elementKey: str, x: np.float64, y: np.float64):
        """
        Sets the insert point of a symbol-object.

        :param elementKey: Key of the symbol-object.
        :type elementKey: str
        :param x: x-coordinate for the object.
        :type x: np.float64
        :param y: y-coordinate for the object.
        :type y: np.float64
        :return: None
        :rtype: None
        :description: Set the insert point of a symbol-object (e.g., Node, Valve, Tank, etc.). The insert point is the position on which the object is placed in the view.
        """
        result, error = self.toolkit.SetInsertPoint(elementKey, x, y)
        if not result:
            print("Error: " + error)
        else:
            print("New point inserted")

    def SetElementColor_RGB(self, elementKey: str, red: int, green: int, blue: int, fillOrLineColor: bool):
        """
        Sets the color of the specified element using RGB values.

        :param elementKey: Key of the symbol-object.
        :type elementKey: str
        :param red: The R-part of the color (0...255).
        :type red: int
        :param green: The G-part of the color (0...255).
        :type green: int
        :param blue: The B-part of the color (0...255).
        :type blue: int
        :param fillOrLineColor: True if the filling color is to be set, False if only the line color is to be set.
        :type fillOrLineColor: bool
        :return: None
        :rtype: None
        :description: This is a wrapper method for SetElementColor() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.SetElementColor(elementKey, red, green, blue, fillOrLineColor)
        if not result:
            print("Error: " + error)
        else:
            print("Color of the element is set")

    def SetElementColor(self, elementKey: str, color: int, fillOrLineColor: bool):
        """
        Sets the color of the specified element using an RGB integer representation.

        :param elementKey: Key of the symbol-object.
        :type elementKey: str
        :param color: The RGB integer representation of the color (COLORREF in GDI).
        :type color: int
        :param fillOrLineColor: True if the filling color is to be set, False if only the line color is to be set.
        :type fillOrLineColor: bool
        :return: None
        :rtype: None
        :description: This is a wrapper method for SetElementColor() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.SetElementColor(elementKey, color, fillOrLineColor)
        if not result:
            print("Error: " + error)
        else:
            print("Color of the element is set")

    def AlignElement(self, elementKey: str):
        """
        Aligns the specified element.

        :param elementKey: Key of the symbol-object.
        :type elementKey: str
        :return: None
        :rtype: None
        :description: This is a wrapper method for AlignElement() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.AlignElement(elementKey)
        if not result:
            print("Error: " + error)
        else:
            print("Alignment successful")

    def GetResultValue(self, elementKey: str, propertyName: str) -> tuple[str, str]:
        """
        Gets the result value for the given element's property.

        :param elementKey: Key of the symbol-object.
        :type elementKey: str
        :param propertyName: The name of the result property.
        :type propertyName: str
        :return: Value for the given element's property and type of the value returned.
        :rtype: tuple[str, str]
        :description: This is a wrapper method for GetResultValue() from toolkit; Watch out for errors for more information.
        """
        result = None
        result, found, valueType, error = self.toolkit.GetResultValue(elementKey, propertyName)
        if result is None:
            print("Error: " + error)
        return result, valueType

    def GetResultProperties_from_elementType(self, elementType, onlySelectedVectors: bool) -> list:
        """
        Gets the result properties for the specified element type.

        :param elementType: The element type.
        :type elementType: Interfaces.Sir3SObjectTypes
        :param onlySelectedVectors: If True, only the names of selected vector channels for this element type shall be returned, otherwise all possible result property names for this element type shall be returned.
        :type onlySelectedVectors: bool
        :return: List of result property names of an element type.
        :rtype: list
        :description: This is a wrapper method for GetResultProperties() from toolkit; Watch out for errors for more information.
        """
        Result_list = None
        Result_list, error = self.toolkit.GetResultProperties(elementType, onlySelectedVectors)
        if Result_list is None:
            print("Error: " + error)
        return list(Result_list)

    def GetResultProperties_from_elementKey(self, elementKey: str) -> list:
        """
        Gets the result properties for the specified element key.

        :param elementKey: The element key.
        :type elementKey: str
        :return: List of all result property names of an element.
        :rtype: list
        :description: This is a wrapper method for GetResultProperties() from toolkit; Watch out for errors for more information.
        """
        Result_list = None
        Result_list, error = self.toolkit.GetResultProperties(elementKey)
        if Result_list is None:
            print("Error: " + error)
        return list(Result_list)

    def GetMinResult(self, elementType, propertyName: str) -> tuple[str, str, str]:
        """
        Gets the minimal result value of an element type and also the key (tk/pk) of the corresponding element.

        :param elementType: The element type.
        :type elementType: Interfaces.Sir3SObjectTypes
        :param propertyName: The name of the result property.
        :type propertyName: str
        :return: The minimal result value of an element type, the key (tk/pk) of the corresponding element, and the data type of the result.
        :rtype: tuple[str, str, str]
        :description: This is a wrapper method for GetMinResult() from toolkit; Watch out for errors for more information.
        """
        MinResult = None
        MinResult, tkElement, valueType, error = self.toolkit.GetMinResult(elementType, propertyName)
        if MinResult is None:
            print("Error: " + error)
        return MinResult, tkElement, valueType
    
    def GetMaxResult(self, elementType, propertyName: str) -> tuple[str, str, str]:
        """
        Gets the maximal result value of an element type and also the key (tk/pk) of the corresponding element.

        :param elementType: The element type.
        :type elementType: Interfaces.Sir3SObjectTypes
        :param propertyName: The name of the result property.
        :type propertyName: str
        :return: The maximal result value of an element type, the key (tk/pk) of the corresponding element, and the data type of the result.
        :rtype: tuple[str, str, str]
        :description: This is a wrapper method for GetMaxResult() from toolkit; Watch out for errors for more information.
        """
        MaxResult = None
        MaxResult, tkElement, valueType, error = self.toolkit.GetMaxResult(elementType, propertyName)
        if MaxResult is None:
            print("Error: " + error)
        return MaxResult, tkElement, valueType

    def GetMinResult_for_timestamp(self, timestamp: str, elementType, propertyName: str) -> tuple[str, str, str]:
        """
        Gets the minimal result value of an element type at a particular timestamp and also the key (tk/pk) of the corresponding element.

        :param timestamp: The timestamp for which result is needed.
        :type timestamp: str
        :param elementType: The element type.
        :type elementType: Interfaces.Sir3SObjectTypes
        :param propertyName: The name of the result property.
        :type propertyName: str
        :return: The minimal result value of an element type at a particular timestamp, the key (tk/pk) of the corresponding element, and the data type of the result.
        :rtype: tuple[str, str, str]
        :description: This is a wrapper method for GetMinResult() from toolkit; Watch out for errors for more information.
        """
        MinResult = None
        MinResult, tkElement, valueType, error = self.toolkit.GetMinResult(timestamp, elementType, propertyName)
        if MinResult is None:
            print("Error: " + error)
        return MinResult, tkElement, valueType

    def GetMaxResult_for_timestamp(self, timestamp: str, elementType, propertyName: str) -> tuple[str, str, str]:
        """
        Gets the maximal result value of an element type at a particular timestamp and also the key (tk/pk) of the corresponding element.

        :param timestamp: The timestamp for which result is needed.
        :type timestamp: str
        :param elementType: The element type.
        :type elementType: Interfaces.Sir3SObjectTypes
        :param propertyName: The name of the result property.
        :type propertyName: str
        :return: The maximal result value of an element type at a particular timestamp, the key (tk/pk) of the corresponding element, and the data type of the result.
        :rtype: tuple[str, str, str]
        :description: This is a wrapper method for GetMaxResult() from toolkit; Watch out for errors for more information.
        """
        MaxResult = None
        MaxResult, tkElement, valueType, error = self.toolkit.GetMaxResult(timestamp, elementType, propertyName)
        if MaxResult is None:
            print("Error: " + error)
        return MaxResult, tkElement, valueType

    def AddNewNode(self, tkCont: str, name: str, typ: str, x: np.float64, y: np.float64, z: np.float32, qm_PH: np.float32, symbolFactor: np.float64, description: str, idRef: str, kvr: int) -> str:
        """
        Inserts a new node.

        :param tkCont: The TK of the container (view) in which the new object shall be inserted. Entering a value of "-1" means the main view of the model.
        :type tkCont: str
        :param name: Name of the new node.
        :type name: str
        :param typ: Type of the new node.
        :type typ: str
        :param x: X coordinate.
        :type x: np.float64
        :param y: Y coordinate.
        :type y: np.float64
        :param z: Geodetic height.
        :type z: np.float32
        :param qm_PH: Value for extraction/feeding (in case QKON) or pressure (in case PKON or PKQN).
        :type qm_PH: np.float32
        :param symbolFactor: The symbol factor of the new node.
        :type symbolFactor: np.float64
        :param description: Description.
        :type description: str
        :param idRef: ID in reference system.
        :type idRef: str
        :param kvr: SL/RL flag. Should be 0 (undefined), 1 (SL) or 2 (RL).
        :type kvr: int
        :return: The key (TK) of the added node, otherwise '-1' if something went wrong.
        :rtype: str
        :description: Comfortable method for inserting a new node.
        """
        Tk_new, error = self.toolkit.AddNewNode(tkCont, name, typ, x, y, z, qm_PH, symbolFactor, description, idRef, kvr)
        if Tk_new == "-1":
            print("Error: " + error)
        else:
            print("New node added")
        return Tk_new

    def AddNewPipe(self, tkCont: str, tkFrom: str, tkTo: str, L: np.float32, linestring: str, material: str, dn: str, roughness: np.float32, idRef: str, description: str, kvr: int) -> str:
        """
        Inserts a new pipe.

        :param tkCont: The TK of the container (view) in which the new object shall be inserted. Entering a value of "-1" means the main view of the model.
        :type tkCont: str
        :param tkFrom: Tk (key) of the start node.
        :type tkFrom: str
        :param tkTo: Tk (key) of the end node.
        :type tkTo: str
        :param L: The pipe length, mandatory for computation.
        :type L: np.float32
        :param linestring: An optional string with intermediate points for geometry formatted like 'LINESTRING (120 76, 500 300, 620 480)'. The insert points of from and to will be added on both ends of the geometry.
        :type linestring: str
        :param material: Name or Tk (key) of the pipe diameter table.
        :type material: str
        :param dn: The nominal diameter or the Tk of the nominal diameter.
        :type dn: str
        :param roughness: Roughness of pipe.
        :type roughness: np.float32
        :param description: Description.
        :type description: str
        :param idRef: ID in reference system.
        :type idRef: str
        :param kvr: SL/RL flag. Should be 0 (undefined), 1 (SL) or 2 (RL).
        :type kvr: int
        :return: The key (TK) of the added pipe, otherwise '-1' if something went wrong.
        :rtype: str
        :description: Comfortable method for inserting a new pipe.
        """
        Tk_new, error = self.toolkit.AddNewPipe(tkCont, tkFrom, tkTo, L, linestring, material, dn, roughness, idRef, description, kvr)
        if Tk_new == "-1":
            print("Error: " + error)
        else:
            print("New pipe added")
        return Tk_new
    
    def AddNewConnectingElement(self, tkCont: str, tkFrom: str, tkTo: str, x: np.float64, y: np.float64, z: np.float32, elementType, dn: np.float32, symbolFactor: np.float64, angleDegree: np.float32, idRef: str, description: str) -> str:
        """
        Inserts a new connecting element.

        :param tkCont: The TK of the container (view) in which the new object shall be inserted. Entering a value of "-1" means the main view of the model.
        :type tkCont: str
        :param tkFrom: Tk (key) of the start node.
        :type tkFrom: str
        :param tkTo: Tk (key) of the end node.
        :type tkTo: str
        :param x: X coordinate.
        :type x: np.float64
        :param y: Y coordinate.
        :type y: np.float64
        :param z: Z coordinate.
        :type z: np.float32
        :param elementType: Element type.
        :type elementType: Interfaces.Sir3SObjectTypes
        :param dn: The nominal diameter or the Tk of the nominal diameter.
        :type dn: np.float32
        :param symbolFactor: The symbol factor of the new node.
        :type symbolFactor: np.float64
        :param angleDegree: The symbol angle in degrees.
        :type angleDegree: np.float32
        :param idRef: ID in reference system.
        :type idRef: str
        :param description: Description.
        :type description: str
        :return: The key (TK) of the added connecting element, otherwise '-1' if something went wrong.
        :rtype: str
        :description: Comfortable method for inserting a new connecting element.
        """
        Tk_new, error = self.toolkit.AddNewConnectingElement(tkCont, tkFrom, tkTo, x, y, z, elementType, dn, symbolFactor, angleDegree, idRef, description)
        if Tk_new == "-1":
            print("Error: " + error)
        else:
            print("New connecting element added")
        return Tk_new

    def AddNewBypassElement(self, tkCont: str, tkFrom: str, x: np.float64, y: np.float64, z: np.float32, symbolFactor: np.float64, elementType, idRef: str, description: str) -> str:
        """
        Inserts a new bypass element.

        :param tkCont: The TK of the container (view) in which the new object shall be inserted. Entering a value of "-1" means the main view of the model.
        :type tkCont: str
        :param tkFrom: Tk (key) of the start node.
        :type tkFrom: str
        :param x: X coordinate.
        :type x: np.float64
        :param y: Y coordinate.
        :type y: np.float64
        :param z: Z coordinate.
        :type z: np.float32
        :param symbolFactor: The symbol factor of the new node.
        :type symbolFactor: np.float64
        :param elementType: Element type.
        :type elementType: Interfaces.Sir3SObjectTypes
        :param idRef: ID in reference system.
        :type idRef: str
        :param description: Description.
        :type description: str
        :return: The key (TK) of the added bypass element, otherwise '-1' if something went wrong.
        :rtype: str
        :description: Comfortable method for inserting a new bypass element.
        """
        Tk_new, error = self.toolkit.AddNewBypassElement(tkCont, tkFrom, x, y, z, symbolFactor, elementType, idRef, description)
        if Tk_new == "-1":
            print("Error: " + error)
        else:
            print("New Bypass element added")
        return Tk_new

    def GetTkFromIDReference(self, IdRef: str, object_type) -> str:
        """
        Extracts the TK of an element using its ID reference.

        :param IdRef: ID reference of the element.
        :type IdRef: str
        :param object_type: Type of the element (like Node, Pipe, Valve, etc.).
        :type object_type: Interfaces.Sir3SObjectTypes
        :return: TK of the element.
        :rtype: str
        :description: This is a wrapper method for GetTkFromIDReference() from toolkit; Watch out for error messages for more information.
        """
        Tk, error = self.toolkit.GetTkFromIDReference(IdRef, object_type)
        if Tk == "-1":
            print("Error: " + error)
        return Tk

    def GetGeometryInformation(self, Tk: str) -> str:
        """
        Extracts the geometry information of an element using its TK.

        :param Tk: TK of the element whose geometry information is needed.
        :type Tk: str
        :return: Geometry information of the element.
        :rtype: str
        :description: This is a wrapper method for GetGeometryInformation() from toolkit; Watch out for error messages for more information.
        """
        geomInfo, error = self.toolkit.GetGeometryInformation(Tk)
        if error != "":
            print("Error: " + error)
        return geomInfo

    def SetGeometryInformation(self, Tk: str, Wkt: str) -> bool:
        """
        Sets the geometry information of an element using its TK.

        :param Tk: TK of the element whose geometry information needs to be set.
        :type Tk: str
        :param Wkt: Geometry information to be set in the format of WKT.
        :type Wkt: str
        :return: True if geometry information is set, False otherwise.
        :rtype: bool
        :description: This is a wrapper method for SetGeometryInformation() from toolkit; Watch out for error messages for more information.
        """
        isSet, error = self.toolkit.SetGeometryInformation(Tk, Wkt)
        if not isSet:
            print("Error: " + error)
        else:
            print("Geometry Information is set correctly")
        return isSet

    def AllowSirMessageBox(self, bAllow: bool):
        """
        Use this method for allowing SIR DB Message Boxes to pop or not

        :param bAllow: Allow/not allow
        :type Tk: bool
        :return: None
        :rtype: None
        :description: This is a wrapper method for AllowSirMessageBox() from toolkit
        """
        self.toolkit.AllowSirMessageBox(bAllow)

    def GetEndNodes(self, Tk: str) -> tuple[str, str, str, str] :
        """
        General Methot for getting the Tk (keys) of Endnodes connected to an Element.
        In SIR 3S, they exists Elements that have:
        Only 1 Endnodes (i.e. Tanks, Air Valves, ...) : Bypass Elements in General
              2 Endnodes (i.e. Pipes, Pumps, Flap Valves, ...): Connecting Elements in General
              4 Endnodes (Heat Exchangers)
        This Method always return for unconnected or non-existent Sides a fkkX Value of '-1'

        :param Tk: The Tk (key) of the Element we need to retrieve the Endnodes
        :type Tk: str
        :return: fkKI, fkKK, fkKI2, fkKK2 
        :rtype: tuple[str, str, str, str]
        :description: This is a wrapper method for GetEndNodes() from toolkit
        """
        returnValue, fkKI, fkKK, fkKI2, fkKK2, error = self.toolkit.GetEndNodes(Tk)
        if not returnValue:
            print("Error: " + error)
        return fkKI, fkKK, fkKI2, fkKK2

"""
Class definition of SIR3S_View() wrapper to access functionalities provided by SIR3S software
This should be used inside python console plugin to give better control over the model for users
"""

class SIR3S_View:

    def __init__(self):
        """
        Create an instance of the Sir3SToolkit class using toolkitfactory provided by Sir3S_Toolkit.dll.

        :description: Initializes the toolkit. If initialization fails, an error message is printed.
        """
        # Basic imports to dlls provided by SirGraf
        # This will only work if Initialize_Toolkit() is called in the same context
        import Sir3S_Repository.ModelManager
        import Sir3S_Repository.Utilities as Util
        import Sir3S_Repository.Interfaces as Interfaces
        import Sir3S_Toolkit.Model as Sir3SToolkit
        
        self.toolkit = Util.StaticUI.Toolkit
        if self.toolkit == None:
            self.toolkit = Sir3SToolkit.CSir3SToolkitFactory.CreateToolkit(None, SIR3S_SIRGRAF_DIR, r"90-15-00-01")
        if (self.toolkit is None):
            print("Error in initializing the toolkit")
        else:
            print("Initialization complete")

    def StartTransaction(self, SessionName: str):
        """
        Start a transaction with the given session name.

        :param SessionName: A meaningful name to start a transaction; Empty string or None will lead to error.
        :type SessionName: str
        :return: None
        :rtype: None
        :description: This method is a wrapper method for StartTransaction() from toolkit.
        """
        isTransactionStarted, message = self.toolkit.StartTransaction(SessionName)
        if not isTransactionStarted:
            print(message)
        else:
            if message == "":
                print("Now you can make changes to the model")
            else:
                print(message)

    def EndTransaction(self):
        """
        End the current transaction.

        :return: None
        :rtype: None
        :description: This method is a wrapper method for EndTransaction() from toolkit. Use it after StartTransaction() to close that transaction.
        """
        isTransactionEnded, message = self.toolkit.EndTransaction()
        if not isTransactionEnded:
            print(message)
        else:
            if message == "":
                print("Transaction has ended. Please open up a new transaction if you want to make further changes")
            else:
                print(message)

    def StartEditSession(self, SessionName: str):
        """
        Start an edit session with the given session name.

        :param SessionName: A meaningful name to start a session.
        :type SessionName: str
        :return: None
        :rtype: None
        :description: This method is a wrapper method for StartEditSession() from toolkit.
        """
        isTransactionStarted, message = self.toolkit.StartEditSession(SessionName)
        if not isTransactionStarted:
            print(message)
        else:
            if message == "":
                print("Now you can make changes to the model")
            else:
                print(message)

    def EndEditSession(self):
        """
        End the current edit session.

        :return: None
        :rtype: None
        :description: This method is a wrapper method for EndEditSession() from toolkit. Use it after StartEditSession() to close that session.
        """
        isTransactionEnded, message = self.toolkit.EndEditSession()
        if not isTransactionEnded:
            print(message)
        else:
            if message == "":
                print("Edit Session has ended. Please open up a new session if you want to make further changes")
            else:
                print(message)

    def SaveChanges(self):
        """
        Saves changes made to the model.

        :return: None
        :rtype: None
        :description: This is a wrapper method for SaveChanges() from toolkit; Use it after End{EditSession/Transaction}. Watch out for errors for more information.
        """
        isSaved, error = self.toolkit.SaveChanges()
        if not isSaved:
            print(f"Error: {error}")
        else:
            print("Changes saved successfully")

    def OpenModelXml(self, Path: str, SaveCurrentModel: bool):
        """
        Opens a model from an XML file.

        :param Path: Path to XML file.
        :type Path: str
        :param SaveCurrentModel: Do you want to save the current model before closing it?
        :type SaveCurrentModel: bool
        :return: None
        :rtype: None
        :description: This is a wrapper method for OpenModelXml() from toolkit; Watch out for error message for more information.
        """
        result, error = self.toolkit.OpenModelXml(Path, SaveCurrentModel)
        if(result == True):
            print("Model is open for further operation")
        else:
            print("Error while opening the model," + error)



    def OpenModel(self, dbName: str, providerType, Mid: str, saveCurrentlyOpenModel: bool, namedInstance: str, userID: str, password: str):
        """
        Opens a model from a database file.

        :param dbName: Full path to the database file.
        :type dbName: str
        :param providerType: Provider type from the enum.
        :type providerType: Interfaces.SirDBProviderType
        :param Mid: Model identifier.
        :type Mid: str
        :param saveCurrentlyOpenModel: Do you want to save the current model before closing it?
        :type saveCurrentlyOpenModel: bool
        :param namedInstance: Instance name of the SQL Server.
        :type namedInstance: str
        :param userID: User Id for Authentication, only needed for ORACLE and for SQLServer only if SQLServer Authentication is required.
        :type userID: str
        :param password: Password for Authentication, only needed for ORACLE and for SQLServer Authentication is required.
        :return: None
        :rtype: None
        :description: This is a wrapper method for openModel() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.OpenModel(dbName, providerType, Mid, saveCurrentlyOpenModel, namedInstance, userID, password)
        if(result == True):
            print("Model is open for further operation")
        else:
            print("Error while opening the model, " + error)

    def GetMainContainer(self):
        """
        Finds the main container of the model and returns its Key (TK).

        :return: Tk of the main container and object type.
        :rtype: tuple[str, Interfaces.Sir3SObjectTypes]
        :description: This is a wrapper method for GetMainContainer() from toolkit; Finds the Main Container of the Model and returns its Key (TK).
        """
        Tk, objType, error = self.toolkit.GetMainContainer()
        if Tk == "-1":
            print("Error: " + error)
        return Tk, objType

    def AddExternalPolyline(self, xArray: list, yArray: list, iColor: int, lineWidthMM: np.float64, dashedLine: bool, containerTK: str) -> str:
        """
        Adds an external polyline.

        :param xArray: List of x coordinates.
        :type xArray: list
        :param yArray: List of y coordinates.
        :type yArray: list
        :param iColor: Color of the polyline.
        :type iColor: int
        :param lineWidthMM: Width of the polyline in mm.
        :type lineWidthMM: np.float64
        :param dashedLine: Boolean indicating if the polyline is dashed.
        :type dashedLine: bool
        :param containerTK: Key of the container.
        :type containerTK: str
        :return: Tk of the added polyline.
        :rtype: str
        :description: This is a wrapper method for AddExternalPolyline() from toolkit; Watch out for errors for more information.
        """
        Tk, error = self.toolkit.AddExternalPolyline(System.String.Empty, xArray, yArray, iColor, lineWidthMM, dashedLine, containerTK)
        if Tk == "-1":
            print("Error: " + error)
        else:
            print("External polyline added")
        return Tk

    def AddExternalPolylinePoint(self, Tk: str, x: np.float64, y: np.float64):
        """
        Adds a point to an external polyline.

        :param Tk: Key of the polyline.
        :type Tk: str
        :param x: x-coordinate of the point.
        :type x: np.float64
        :param y: y-coordinate of the point.
        :type y: np.float64
        :return: None
        :rtype: None
        :description: This is a wrapper method for AddExternalPolylinePoint() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.AddExternalPolylinePoint(Tk, x, y, System.String.Empty)
        if not result:
            print("Error: " + error)
        else:
            print("External poly line point added")

    def SetExternalPolyLineWidthAndColor(self, Tk: str, lineWidthMM: np.float64, iColor: int):
        """
        Sets the width and color of an external polyline.

        :param Tk: Key of the polyline.
        :type Tk: str
        :param lineWidthMM: Width of the polyline in mm.
        :type lineWidthMM: np.float64
        :param iColor: Color of the polyline.
        :type iColor: int
        :return: None
        :rtype: None
        :description: This is a wrapper method for AddExternalPolylinePoint() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.SetExternalPolyLineWidthAndColor(Tk, lineWidthMM, iColor, System.String.Empty)
        if not result:
            print("Error: " + error)
        else:
            print("External polyline width and color are set")

    def AddExternalPolygon(self, xArray: list, yArray: list, lineColor: int, fillColor: int, lineWidthMM: np.float64, isFilled: bool, containerTK: str) -> str:
        """
        Adds an external polygon.

        :param xArray: List of x coordinates.
        :type xArray: list
        :param yArray: List of y coordinates.
        :type yArray: list
        :param lineColor: Color of the polygon's line.
        :type lineColor: int
        :param fillColor: Fill color of the polygon.
        :type fillColor: int
        :param lineWidthMM: Width of the polygon's line in mm.
        :type lineWidthMM: np.float64
        :param isFilled: Boolean indicating if the polygon is filled.
        :type isFilled: bool
        :param containerTK: Key of the container.
        :type containerTK: str
        :return: Tk of the added polygon.
        :rtype: str
        :description: This is a wrapper method for AddExternalPolygon() from toolkit; Watch out for errors for more information.
        """
        Tk, error = self.toolkit.AddExternalPolygon(System.String.Empty, xArray, yArray, lineColor, fillColor, lineWidthMM, isFilled, containerTK)
        if Tk == "-1":
            print("Error: " + error)
        else:
            print("External polygon is added")
        return Tk

    def AddExternalPolygonPoint(self, Tk: str, x: np.float64, y: np.float64):
        """
        Adds a point to an external polygon.

        :param Tk: Key of the polygon.
        :type Tk: str
        :param x: x-coordinate of the point.
        :type x: np.float64
        :param y: y-coordinate of the point.
        :type y: np.float64
        :return: None
        :rtype: None
        :description: This is a wrapper method for AddExternalPolygonPoint() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.AddExternalPolygonPoint(Tk, x, y, System.String.Empty)
        if not result:
            print("Error: " + error)
        else:
            print("External polygon point added")

    def SetExternalPolygonProperties(self, Tk: str, lineWidthMM: np.float64, lineColor: int, fillColor: int, isFilled: bool):
        """
        Sets properties of an external polygon.

        :param Tk: Key of the polygon.
        :type Tk: str
        :param lineWidthMM: Width of the polygon's line in mm.
        :type lineWidthMM: np.float64
        :param lineColor: Color of the polygon's line.
        :type lineColor: int
        :param fillColor: Fill color of the polygon.
        :type fillColor: int
        :param isFilled: Boolean indicating if the polygon is filled.
        :type isFilled: bool
        :return: None
        :rtype: None
        :description: This is a wrapper method for SetExternalPolygonProperties() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.SetExternalPolygonProperties(Tk, lineWidthMM, lineColor, fillColor, isFilled, System.String.Empty)
        if not result:
            print("Error: " + error)
        else:
            print("External polygon properties are set")

    def AddExternalText(self, x: np.float64, y: np.float64, textColor: int, text: str, angleDegree: np.float32, heightPt: np.float32,
                        isBold: bool, isItalic: bool, isUnderline: bool, containerTK: str):
        """
        Adds external text.

        :param x: x-coordinate of the text.
        :type x: np.float64
        :param y: y-coordinate of the text.
        :type y: np.float64
        :param textColor: Color of the text.
        :type textColor: int
        :param text: The text content.
        :type text: str
        :param angleDegree: Angle of the text in degrees.
        :type angleDegree: np.float32
        :param heightPt: Height of the text in points.
        :type heightPt: np.float32
        :param isBold: Boolean indicating if the text is bold.
        :type isBold: bool
        :param isItalic: Boolean indicating if the text is italic.
        :type isItalic: bool
        :param isUnderline: Boolean indicating if the text is underlined.
        :type isUnderline: bool
        :param containerTK: Key of the container.
        :type containerTK: str
        :return: Tk of the added text.
        :rtype: str
        :description: This is a wrapper method for AddExternalText() from toolkit; Watch out for errors for more information.
        """
        Tk, error = self.toolkit.AddExternalText(System.String.Empty, x, y, textColor, text, angleDegree, heightPt, isBold, isItalic, isUnderline, containerTK)
        if Tk == "-1":
            print("Error: " + error)
        else:
            print("External text is added")
        return Tk
    
    def SetExternalTextText(self, Tk: str, text: str):
        """
        Sets the text of an external text element.

        :param Tk: Key of the text element.
        :type Tk: str
        :param text: The text content.
        :type text: str
        :return: None
        :rtype: None
        :description: This is a wrapper method for SetExternalTextText() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.SetExternalTextText(Tk, text, System.String.Empty)
        if not result:
            print("Error: " + error)
        else:
            print("External text is set")

    def SetExternalTextProperties(self, Tk: str, x: np.float64, y: np.float64, textColor: int, text: str, angleDegree: np.float32, heightPt: np.float32,
                        isBold: bool, isItalic: bool,isUnderline: bool):
        """
        Sets properties of an external text element.

        :param Tk: Key of the text element.
        :type Tk: str
        :param x: x-coordinate of the text.
        :type x: np.float64
        :param y: y-coordinate of the text.
        :type y: np.float64
        :param textColor: Color of the text.
        :type textColor: int
        :param text: The text content.
        :type text: str
        :param angleDegree: Angle of the text in degrees.
        :type angleDegree: np.float32
        :param heightPt: Height of the text in points.
        :type heightPt: np.float32
        :param isBold: Boolean indicating if the text is bold.
        :type isBold: bool
        :param isItalic: Boolean indicating if the text is italic.
        :type isItalic: bool
        :param isUnderline: Boolean indicating if the text is underlined.
        :type isUnderline: bool
        :return: None
        :rtype: None
        :description: This is a wrapper method for SetExternalTextProperties() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.SetExternalTextProperties(Tk, x, y,System.String.Empty, textColor, text, angleDegree, heightPt, isBold, isItalic, isUnderline)
        if not result:
            print("Error: " + error)
        else:
            print("External text properties are set")

    def AddExternalArrow(self, x: np.float64, y: np.float64, lineColor: int, fillColor: int, lineWidthMM: np.float64, 
                            isFilled: bool, symbolFactor: np.float64, containerTK: str):
        """
        Adds an external arrow.

        :param x: x-coordinate of the arrow.
        :type x: np.float64
        :param y: y-coordinate of the arrow.
        :type y: np.float64
        :param lineColor: Color of the arrow's line.
        :type lineColor: int
        :param fillColor: Fill color of the arrow.
        :type fillColor: int
        :param lineWidthMM: Width of the arrow's line in mm.
        :type lineWidthMM: np.float64
        :param isFilled: Boolean indicating if the arrow is filled.
        :type isFilled: bool
        :param symbolFactor: Symbol factor of the arrow.
        :type symbolFactor: np.float64
        :param containerTK: Key of the container.
        :type containerTK: str
        :return: Tk of the added arrow.
        :rtype: str
        :description: This is a wrapper method for AddExternalArrow() from toolkit; Watch out for errors for more information.
        """
        Tk, error = self.toolkit.AddExternalArrow(System.String.Empty,x, y, lineColor, fillColor, lineWidthMM, isFilled, symbolFactor, containerTK)
        if Tk == "-1":
            print("Error : " + error)
        else:
            print("External arrow added")
        return Tk

    def SetExternalArrowProperties(self, Tk: str, x: np.float64, y: np.float64, lineColor: int, fillColor: int, lineWidthMM: np.float64, 
                            isFilled: bool, symbolFactor: np.float64):
        """
        Sets properties of an external arrow element.

        :param Tk: Key of the arrow element.
        :type Tk: str
        :param x: x-coordinate of the arrow element.
        :type x: np.float64
        :param y: y-coordinate of the arrow element.
        :type y: np.float64
        :param lineColor: Color of the arrow's line.
        :type lineColor: int
        :param fillColor: Fill color of the arrow element.
        :type fillColor: int
        :param lineWidthMM: Width of the arrow's line in mm.
        :type lineWidthMM: np.float64
        :param isFilled: Boolean indicating if the arrow element is filled.
        :type isFilled: bool
        :param symbolFactor: Symbol factor of the arrow element.
        :type symbolFactor: np.float64
        :return: None
        :rtype: None
        :description: This is a wrapper method for AddExternalArrow() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.SetExternalArrowProperties(Tk, System.String.Empty, x, y, lineColor, fillColor, lineWidthMM, isFilled, symbolFactor)
        if not result:
            print("Error: " + error)
        else:
            print("External arrow properties are set")

    def AddExternalRectangle(self, left: np.float64, top: np.float64, right: np.float64, bottom: np.float64,
                                lineColor: int, fillColor: int, lineWidthMM: np.float64, 
                                isFilled: bool, isRounded: bool, containerTK: str):
        """
        Adds an external rectangle element.

        :param left: Left coordinate of the rectangle.
        :type left: np.float64
        :param top: Top coordinate of the rectangle.
        :type top: np.float64
        :param right: Right coordinate of the rectangle.
        :type right: np.float64
        :param bottom: Bottom coordinate of the rectangle.
        :type bottom: np.float64
        :param lineColor: Color of the rectangle's line.
        :type lineColor: int
        :param fillColor: Fill color of the rectangle.
        :type fillColor: int
        :param lineWidthMM: Width of the rectangle's line in mm.
        :type lineWidthMM: np.float64
        :param isFilled: Boolean indicating if the rectangle is filled.
        :type isFilled: bool
        :param isRounded: Boolean indicating if the rectangle is rounded.
        :type isRounded: bool
        :param containerTK: Key of the container.
        :type containerTK: str
        :return: Tk of the added rectangle.
        :rtype: str
        :description: This is a wrapper method for AddExternalRectangle() from toolkit; Watch out for errors for more information.
        """
        Tk, error = self.toolkit.AddExternalRectangle(System.String.Empty,left, top, right, bottom, lineColor, fillColor, lineWidthMM, isFilled, isRounded, containerTK)
        if Tk == "-1":
            print("Error : " + error)
        else:
            print("External rectangle is added")
        return Tk

    def SetExternalRectangleProperties(self, Tk: str, left: np.float64, top: np.float64, right: np.float64, bottom: np.float64,
                                lineColor: int, fillColor: int, lineWidthMM: np.float64, 
                                isFilled: bool, isRounded: bool):
        """
        Sets properties of an external rectangle element.

        :param Tk: Key of the rectangle element.
        :type Tk: str
        :param left: Left coordinate of the rectangle.
        :type left: np.float64
        :param top: Top coordinate of the rectangle.
        :type top: np.float64
        :param right: Right coordinate of the rectangle.
        :type right: np.float64
        :param bottom: Bottom coordinate of the rectangle.
        :type bottom: np.float64
        :param lineColor: Color of the rectangle's line.
        :type lineColor: int
        :param fillColor: Fill color of the rectangle.
        :type fillColor: int
        :param lineWidthMM: Width of the rectangle's line in mm.
        :type lineWidthMM: np.float64
        :param isFilled: Boolean indicating if the rectangle is filled.
        :type isFilled: bool
        :param isRounded: Boolean indicating if the rectangle is rounded.
        :type isRounded: bool
        :return: None
        :rtype: None
        :description: This is a wrapper method for SetExternalRectangleProperties() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.SetExternalRectangleProperties(Tk, System.String.Empty, left, top, right, bottom, lineColor, fillColor, lineWidthMM, isFilled, isRounded)
        if not result:
            print("Error: " + error)
        else:
            print("External rectangle properties are set")

    def AddExternalEllipse(self, left: np.float64, top: np.float64, right: np.float64, bottom: np.float64,
                                lineColor: int, fillColor: int, lineWidthMM: np.float64, 
                                isFilled: bool, containerTK: str) -> str:
        """
        Adds an external ellipse element.

        :param left: Left coordinate of the ellipse.
        :type left: np.float64
        :param top: Top coordinate of the ellipse.
        :type top: np.float64
        :param right: Right coordinate of the ellipse.
        :type right: np.float64
        :param bottom: Bottom coordinate of the ellipse.
        :type bottom: np.float64
        :param lineColor: Color of the ellipse's line.
        :type lineColor: int
        :param fillColor: Fill color of the ellipse.
        :type fillColor: int
        :param lineWidthMM: Width of the ellipse's line in mm.
        :type lineWidthMM: np.float64
        :param isFilled: Boolean indicating if the ellipse is filled.
        :type isFilled: bool
        :param containerTK: Key of the container.
        :type containerTK: str
        :return: Tk of the added ellipse.
        :rtype: str
        :description: This is a wrapper method for AddExternalEllipse() from toolkit; Watch out for errors for more information.
        """
        Tk, error = self.toolkit.AddExternalEllipse(System.String.Empty, left, top, right, bottom, lineColor, fillColor, lineWidthMM, isFilled, containerTK)
        if Tk == "-1":
            print("Error : " + error)
        else:
            print("External ellipse is added")
        return Tk

    def SetExternalEllipseProperties(self, Tk: str, left: np.float64, top: np.float64, right: np.float64, bottom: np.float64,
                                lineColor: int, fillColor: int, lineWidthMM: np.float64,  isFilled: bool):
        """
        Sets properties of an external ellipse element.

        :param Tk: Key of the ellipse element.
        :type Tk: str
        :param left: Left coordinate of the ellipse.
        :type left: np.float64
        :param top: Top coordinate of the ellipse.
        :type top: np.float64
        :param right: Right coordinate of the ellipse.
        :type right: np.float64
        :param bottom: Bottom coordinate of the ellipse.
        :type bottom: np.float64
        :param lineColor: Color of the ellipse's line.
        :type lineColor: int
        :param fillColor: Fill color of the ellipse.
        :type fillColor: int
        :param lineWidthMM: Width of the ellipse's line in mm.
        :type lineWidthMM: np.float64
        :param isFilled: Boolean indicating if the ellipse is filled.
        :type isFilled: bool
        :return: None
        :rtype: None
        :description: This is a wrapper method for SetExternalEllipseProperties() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.SetExternalEllipseProperties(Tk, System.String.Empty, left, top, right, bottom, lineColor, fillColor, lineWidthMM, isFilled)
        if not result:
            print("Error: " + error)
        else:
            print("External ellipse properties are set")

    def PrepareColoration(self):
        """
        Prepares coloration for elements.

        :return: None
        :rtype: None
        :description: This is a wrapper method for PrepareColoration() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.PrepareColoration(System.String.Empty)
        if not result:
            print("Error: " + error)
        else:
            print("Prepare coloration is done")

    def InitColorTable(self, iColors: list, maxColors: int) -> bool:
        """
        Initializes color table with specified colors and maximum colors.

        :param iColors: List of colors to initialize table with.
        :type iColors: list
        :param maxColors: Maximum number of colors in table.
        :type maxColors: int
        :return: Boolean indicating if color table was initialized successfully.
        :rtype: bool
        :description: This is a wrapper method for InitColorTable() from toolkit; Watch out for errors for more information.
        """
        return self.toolkit.InitColorTable(iColors, maxColors)

    def GetColor(self, valMin: np.float64, valMax: np.float64, val: np.float64) -> tuple[int, int]:
        """
        Gets color corresponding to specified value within range defined by minimum and maximum values.

        :param valMin: Minimum value in range.
        :type valMin: np.float64
        :param valMax: Maximum value in range.
        :type valMax: np.float64
        :param val: Value to get color for within range defined by min and max values.
        :type val: np.float64
        :return: Color corresponding to specified value within range defined by min and max values and index of color in table.
        :rtype: tuple[int, int]
        :description: This is a wrapper method for GetColor() from toolkit; Watch out for errors for more information.
        """
        color, idx = self.toolkit.GetColor(valMin, valMax, val, System.Int32(-1))
        return color, idx
        
    def GetColorTableEntries(self, result_i: np.float64, result_k: np.float64, scaleMin: np.float64, scaleMax: np.float64) -> list:
        """
        Gets color table entries.

        :param result_i: Result i value.
        :type result_i: np.float64
        :param result_k: Result k value.
        :type result_k: np.float64
        :param scaleMin: Minimum scale value.
        :type scaleMin: np.float64
        :param scaleMax: Maximum scale value.
        :type scaleMax: np.float64
        :return: List of color table entries.
        :rtype: list
        :description: This is a wrapper method for GetColorTableEntries() from toolkit; Watch out for errors for more information.
        """
        return self.toolkit.GetColorTableEntries(result_i, result_k, scaleMin, scaleMax)

    def SetWidthScaleProperties(self, valMin: np.float64, widthMin: np.float64, valMax: np.float64, widthMax: np.float64) -> bool:
        """
        Sets width scale properties.

        :param valMin: Minimum value.
        :type valMin: np.float64
        :param widthMin: Minimum width.
        :type widthMin: np.float64
        :param valMax: Maximum value.
        :type valMax: np.float64
        :param widthMax: Maximum width.
        :type widthMax: np.float64
        :return: Boolean indicating if width scale properties were set successfully.
        :rtype: bool
        :description: This is a wrapper method for SetWidthScaleProperties() from toolkit; Watch out for errors for more information.
        """
        return self.toolkit.SetWidthScaleProperties(valMin, widthMin, valMax, widthMax)

    def GetWidthFactor(self, actualValue: np.float64) -> np.float64:
        """
        Gets width factor corresponding to specified actual value.

        :param actualValue: Value to get width factor for.
        :type actualValue: np.float64
        :return: Width factor corresponding to specified actual value.
        :rtype: np.float64
        :description: This is a wrapper method for GetWidthFactor() from toolkit; Watch out for errors for more information.
        """
        return self.toolkit.GetWidthFactor(actualValue)

    def ColoratePipe(self, Tk: str, lengths: list, Colors: list, widthFactors: list):
        """
        Colorates pipe with specified lengths, colors and width factors.

        :param Tk: Key of pipe element.
        :type Tk: str
        :param lengths: List of lengths to colorate pipe with.
        :type lengths: list
        :param Colors: List of colors to colorate pipe with.
        :type Colors: list
        :param widthFactors: List of width factors to colorate pipe with.
        :type widthFactors: list
        :return: None
        :rtype: None
        :description: This is a wrapper method for ColoratePipe() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.ColoratePipe(Tk, lengths, Colors, System.String.Empty, widthFactors)
        if not result:
            print("Error: " + error)
        else:
            print("Colorating pipe is successful")

    def ResetColoration(self):
        """
        Resets coloration of elements.

        :return: None
        :rtype: None
        :description: This is a wrapper method for ResetColoration() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.ResetColoration(System.String.Empty)
        if not result:
            print("Error: " + error)
        else:
            print("Coloration reset is successful")

    def DoColoration(self):
        """
        Performs coloration of elements.
        
        :return: None
        :rtype: None
        :description: This is a wrapper method for DoColoration() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.DoColoration(System.String.Empty)
        if not result:
            print("Error: " + error)
        else:
            print("Coloration is done")

    def MoveElementTo(self, Tk: str, newX: np.float64, newY: np.float64):
        """
        General Method for moving an Object to a specified ABSOLUTE Location.
        This Method only applies to Symbol-Objects (and Texts). 
        Thus Calling it on Line Objects such as Pipes, Polylines, Polygones
        has no effect.

        :param Tk: The tk (key) of the Element
        :type Tk: str
        :param newX: New absolute X-Position
        :type newX: np.float64
        :param newY: New absolute Y-Position
        :type newY: np.float64
        :return: None
        :rtype: None
        :description: This is a wrapper method for MoveElementTo() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.MoveElementTo(Tk, newX, newY)
        if not result:
            print("Error: " + error)
            
    def MoveElementBy(self, Tk: str, dX: np.float64, dY: np.float64):
        """
        General Method for moving an Object by a defined (relative) Amount.
        This Method only applies to both Symbol-Objects (incl. Texts) and also 
        to Line Objects such as Pipes, Polylines, Polygones.
        Calling this Method on a Pipe would also move the both End Nodes of the Pipe.

        :param Tk: The tk (key) of the Element
        :type Tk: str
        :param dX: The Amount of Translation in X-Direction
        :type dX: np.float64
        :param dY: The Amount of Translation in Y-Direction
        :type dY: np.float64
        :return: None
        :rtype: None
        :description: This is a wrapper method for MoveElementBy() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.MoveElementBy(Tk, dX, dY)
        if not result:
            print("Error: " + error)

    
    def AddNewText(self, tkCont: str, x: np.float64, y: np.float64, color: int, textContent: str, 
                   angle_degree: np.float32, faceName: str, heightPt: np.float32, isBold: bool, 
                   isItalic: bool, isUnderlined: bool, idRef: str, description: str) -> str:
        """
        Method for inserting a new Text within a Container

        :param tkCont: The (tk) key of the Container to insert the Text in
        :type tkCont: str
        :param x: Absolute x-Coordinate of the Text (left)
        :type x np.float64
        :param y: Absolute y-Coordinate of the Text (bottom)
        :type y: np.float64
        :param color: The desired Color as RGB
        :type color: int
        :param textContent: The textual Content of the Text. Max 80 Characters
        :type textContent: str
        :param angle_degree: Angle in Degree
        :type angle_degree: np.float32
        :param faceName: Face Name of the Font (max. 32 Characters). Entering a non-installed 
        Face Name will assume it to be 'Arial'
        :type faceName: str
        :param heightPt: The height in Point
        :type heightPt: np.float32
        :param isBold: True if the Font should be bold
        :type isBold: bool
        :param isItalic: True if the Font should be italic
        :type isItalic: bool
        :param isUnderlined: True if the Font should be underlined
        :type isUnderlined: bool
        :param idRef: user-defined Reference ID. Max 40 Characters
        :type idRef: str
        :param description: Description of Text. Max 254 Characters
        :type description: str
        :return: The TK of the newly inserted Text, otherwise '-1'.
        :rtype: str
        :description: This is a wrapper method for AddNewText() from toolkit; Watch out for errors for more information.
        """  
        Tk, error = self.toolkit.AddNewText(tkCont, x, y, color, textContent, angle_degree, 
                                            faceName, heightPt, isBold, isItalic, isUnderlined, idRef, description)
        if Tk == "-1":
            print("Error : " + error)
        return Tk
    
    def GetTextProperties(self, Tk: str) -> textProperties:
        """
        Method for getting Properties of a Text

        :param Tk: The tk (key) of the Element
        :type Tk: str
        :return: return all text properties bundled in a namedtuple 'textProperties'
        :rtype: textProperties
        :description: This is a wrapper method for GetTextProperties() from toolkit; Watch out for errors for more information.
        """
        result, error, x, y, color, textContent, angle_degree, faceName, heightPt, isBold, isItalic, isUnderline, idRef, description = self.toolkit.GetTextProperties(Tk)
        if not result:
            print("Error: " + error)
        return textProperties(x=x,y=y, color=color, textContent=textContent, angle_degree=angle_degree, faceName=faceName, heightPt=heightPt, isBold=isBold, isItalic=isItalic, isUnderline=isUnderline, idRef=idRef, description=description)

    def AddNewNumericalDisplay(self, tkCont: str, x: np.float64, y: np.float64, color: int, 
                   angle_degree: np.float32, faceName: str, heightPt: np.float32, isBold: bool, 
                   isItalic: bool, isUnderlined: bool, description: str, forResult: bool, tkObserved: str, 
                   elemPropertyNameOrResult: str, prefix: str, unit: str, numDec: int, absValue: bool) -> str:
        """
        Method for inserting a new numerical Display into a Container

        :param tkCont: The (tk) key of the Container to insert the numerical Display in
        :type tkCont: str
        :param x: Absolute x-Coordinate of the numerical Displa (left)
        :type dX: np.float64
        :param dY: Absolute y-Coordinate of the numerical Displa (bottom)
        :type dY: np.float64
        :param color: The desired Color as RGB
        :type color: int
        :param angle_degree: Angle in Degree
        :type angle_degree: np.float32
        :param faceName: Face Name of the Font (max. 32 Characters). Entering a non-installed 
        Face Name will assume it to be 'Arial'
        :type faceName: str
        :param heightPt: The height in Point
        :type heightPt: np.float32
        :param isBold: True if the Font should be bold
        :type isBold: bool
        :param isItalic: True if the Font should be italic
        :type isItalic: bool
        :param isUnderlined: True if the Font should be underlined
        :type isUnderlined: bool
        :param description: Description of Text. Max 254 Characters
        :type description: str
        :param forResult: True if it should display a Calculation Result of an Element, False if it
        should display an Element Property
        :type forResult: bool
        :param tkObserved: The tk (Key) of the Element observed by this num. Display
        :type tkObserved: str
        :param elemPropertyNameOrResult: a String representing the Result-Property or the 
        Element Property Name, depending on Parameter 'forResult'.
        eg. "L" if a Pipe Length is observed or "QMAV" for the Result 'Average Flow Rate' on Pipe.
        :type elemPropertyNameOrResult: str
        :param prefix: Prefix (precedes the Text), max. 80 Characters
        :type prefix: str
        :param unit: User-defined Unit, max. 80 Characters
        :type unit: str
        :param numDec: Number of Decimals Digits
        :type numDec: str
        :param absValue: True if a absolute Value should be displayed
        :type absValue: bool
        :return: The TK of the newly inserted numerical display, otherwise '-1'.
        :rtype: str
        :description: This is a wrapper method for AddNewNumericalDisplay() from toolkit; Watch out for errors for more information.
        """  
        Tk, error = self.toolkit.AddNewNumericalDisplay(tkCont, x, y, color, angle_degree, 
                                            faceName, heightPt, isBold, isItalic, isUnderlined, description, forResult, tkObserved, 
                                            elemPropertyNameOrResult, prefix, unit, numDec, absValue)
        if Tk == "-1":
            print("Error : " + error)
        return Tk

    def AddNewDirectionalArrow(self, tkCont: str, x: np.float64, y: np.float64, lineColor: int, lineWidth: np.float64, fillColor: int,   
                            isFilled: bool, symbolFactor: np.float64, description: str, tkObserved: str, elemResultProperty: str, EPS:np.float32):
        """
        Adds an external arrow.

        :param tkCont: The (tk) key of the Container
        :type tkCont: str
        :param x: x-coordinate of the directional arrow.
        :type x: np.float64
        :param y: y-coordinate of the directional arrow.
        :type y: np.float64
        :param lineColor: Color of the directional arrow's line.
        :type lineColor: int
        :param lineWidth: Width of the arrow's line in mm.
        :type lineWidth: np.float64
        :param fillColor: Fill color of the arrow.
        :type fillColor: int
        :param isFilled: Boolean indicating if the arrow is filled.
        :type isFilled: bool
        :param symbolFactor: Symbol factor of the arrow.
        :type symbolFactor: np.float64
        :param description: The Description, max 254 Characters
        :type description: str
        :param tkObserved: The Tk (key) of the Element this array shall be bound to
        :type tkObserved: str
        :param elemResultProperty: The Property Name of a Result on the bound Element
        :type elemResultProperty: str
        :param EPS: Display Tolerance.
        Arrow direction is only displayed if the absolute value of the data point Result value is greater
        than the specified tolerance
        :type EPS: np.float32
        :return: Tk of the added directional arrow.
        :rtype: str
        :description: This is a wrapper method for AddNewDirectionalArrow() from toolkit; Watch out for errors for more information.
        """
        Tk, error = self.toolkit.AddNewDirectionalArrow(tkCont, x, y, lineColor, lineWidth, fillColor, isFilled, symbolFactor, 
                                                        description, tkObserved, elemResultProperty, EPS)
        if Tk == "-1":
            print("Error : " + error)
        return Tk

    def GetNumericalDisplayProperties(self, Tk:str) -> numericalDisplayProperties:
        """
        Method for getting Properties of a numerical display

        :param Tk: The tk (key) of the Element
        :type Tk: str
        :return: return all the properties bundled in a namedtuple 'numericalDisplayProperties'
        :rtype: numericalDisplayProperties
        :description: This is a wrapper method for GetNumericalDisplayProperties() from toolkit; Watch out for errors for more information.
        """
        result, x, y, color, angle_degree, faceName, heightPt, isBold, isItalic, isUnderline, description, forResult, tkObserved, elemPropertyNameOrResult, prefix, unit, numDec, absValue, error = self.toolkit.GetNumericalDisplayProperties(Tk)
        if not result:
            print("Error: " + error)
        return numericalDisplayProperties(x=x,y=y, color=color, angle_degree=angle_degree, faceName=faceName, heightPt=heightPt, isBold=isBold, isItalic=isItalic, isUnderline=isUnderline, description=description, forResult=forResult, tkObserved=tkObserved, elemPropertyNameOrResult=elemPropertyNameOrResult,
                              prefix=prefix, unit=unit, numDec=numDec, absValue=absValue)

    def SetFont(self, Tk: str, textContent: str, color: int, 
                   angle_degree: np.float32, faceName: str, heightPt: np.float32, isBold: bool, isItalic: bool, isUnderlined: bool):
        """
        Sets the Font on a Element that has Font.
        This Method only applies to Texts, numerical Displays, Block Symbols and Block References.

        :param Tk: The tk (key) of the Element which Font has to be retrieved
        :type Tk: str
        :param color: The desired Color as RGB
        :type color: int
        :param textContent: Only has Effect on TEXTs
        :type textContent: str
        :param angle_degree: Text angle
        :type angle_degree: np.float32
        :param faceName: Face Name of the Font 
        :type faceName: str
        :param heightPt: The height in Point
        :type heightPt: np.float32
        :param isBold: True if the Font should be bold
        :type isBold: bool
        :param isItalic: True if the Font should be italic
        :type isItalic: bool
        :param isUnderlined: True if the Font should be underlined
        :type isUnderlined: bool
        :return: None
        :rtype: None
        :description: This is a wrapper method for SetFont() from toolkit; Watch out for errors for more information.
        """
        result, error = self.toolkit.SetFont(Tk, textContent, color, angle_degree, faceName, heightPt, isBold, isItalic, isUnderlined)
        if not result:
            print("Error: " + error)
        else:
            print("Font is set")
            

    def GetFont(self, Tk: str) -> fontInformation:
        """
        Method for getting font related information

        :param Tk: The tk (key) of the Element
        :type Tk: str
        :return: return all the properties bundled in a namedtuple 'fontInformation'
        :rtype: fontInformation
        :description: This is a wrapper method for GetFont() from toolkit; Watch out for errors for more information.
        """
        result, textContent, color, angle_degree, faceName, heightPt, isBold, isItalic, isUnderline, error = self.toolkit.GetFont(Tk)
        if not result:
            print("Error: " + error)
        return fontInformation(textContent=textContent, color=color, angle_degree=angle_degree, faceName=faceName, heightPt=heightPt, isBold=isBold, isItalic=isItalic, isUnderline=isUnderline)

    def AddNewStreet(self, name:str, number:str, place:str, district:str, idref:str) -> str:
        """
        Method for adding a new Street

        :param name: Street Name, max. 80 Characters
        :type name: str
        :param number: Street Number, max. 80 characters (it may be a official Number) 
        :type number: str
        :param place: The name of the Place hosting the Street, max. 80 characters
        :type place: str
        :param district: The name of the District under the Place, max. 80 characters
        :type district: str
        :param idref: Reference ID, max. 40 characters
        :type idref: str
        :return: returns the TK of the newly inserted Street, otherwise '-1'.
        :rtype: str
        :description: This is a wrapper method for AddNewStreet() from toolkit; Watch out for errors for more information.
        """
        Tk, error = self.toolkit.AddNewStreet(name, number, place, district, idref)
        if Tk == "-1":
            print("Error : " + error)
        return Tk
    

    def AddNewHouse(self, x: np.float64, y: np.float64, symbolFactor: np.float64, fkStreet: str, houseNumber: int, numberSuffix: int, 
                    postalCode: int, dsn: str, fkNode: str, fkDH_Customer: str, idRef: str):
        """
        Method for inserting a new House within the main Container of the Model

        :param x: Absolute x-Coordinate of the House
        :type x: np.float64
        :param y: Absolute y-Coordinate of the House
        :type y: np.float64
        :param symbolFactor: The Symbol Factor
        :type symbolFactor: np.float64
        :param fkStreet: The tk (Key) of the Street if any (or just an emty String ot '-1' if none)
        :type fkStreet: str
        :param houseNumber: The House number
        :type houseNumber: int
        :param numberSuffix: The house Number Suffix, max. 40 characters
        :type numberSuffix: int
        :param postalCode: The Postal Code
        :type postalCode: int
        :param dsn: The official Number of the Street (if known), max. 80 Characters
        :type dsn: str
        :param fkNode: Only for non-District Heating Networks: The tk (key) of the Node connected to the House (if any)
        :type fkNode: str
        :param fkDH_Customer: Only for District Heating Networks: The tk (key) of the DH Consumer connected to the House (if any)
        :type fkDH_Customer: str
        :param idRef: User-defined Reference ID
        :type idRef: str
        :return: returns the TK of the newly inserted House, otherwise '-1'.
        :rtype: str
        :description: This is a wrapper method for AddNewHouse() from toolkit; Watch out for errors for more information.
        """
        Tk, error = self.toolkit.AddNewHouse(x, y, symbolFactor,fkStreet, houseNumber, numberSuffix, postalCode, 
                                             dsn, fkNode, fkDH_Customer, idRef)
        if Tk == "-1":
            print("Error : " + error)
        return Tk        


    def AddNewCustomer(self, x: np.float64, y: np.float64,  z: np.float32, symbolFactor: np.float64, fkHouse: str, consumption: np.float64,
            counterId: str, customerId: str, dimension: str, divisionType: str, customerGroup: str, idRef: str) -> str:
        """
        Method for inserting a new Customer within the main Container of the Model

        :param x: Absolute x-Coordinate of the Customer
        :type x: np.float64
        :param y: Absolute y-Coordinate of the Customer
        :type y: np.float64
        :param z: Absolute z-Coordinate of the Customer
        :type z: np.float32
        :param symbolFactor: The Symbol Factor
        :type symbolFactor: np.float64
        :param fkHouse: The tk (Key) of the House the Customer is attached to (or empty String or '-1' if none)
        :type fkHouse: str
        :param consumption:  Consumption Value Q0 (NODE) or W0 (DH-Consumer).
        The consumption Value can have different Dimensions.In Water usually Qa - i.e. [m^3/ a]. In Gas[Nm^3/ a]. In heat, it is usually a power in [kW] or[MW].
        :type consumption: np.float64
        :param counterId: ID point of consumption (from reference data for identification). max 40 Characters
        :type counterId: str
        :param customerId: ID of the Customer who is the contractual Partner of the CC for this point of consumption (from reference data for identification). max 40 Characters 
        :type customerId: str
        :param dimension: Dimension of consumption m3/a, Nm3/a, kW, kWh, MW or MWh, max 12 Characters
        :type dimension: str
        :param divisionType: Division type, max 12 Characters ( should be 'W-', 'W+', 'F-', 'G-' or 'K-' depending on Netrworkm type); 
            W- = consumer in the water network (outflow); 
            W+ = "consumer" in the collection network (inflow); 
            F- = consumer in the district heating network (W0); 
            G- = consumer in the gas network (outflow); 
            K- = consumer in the refrigeration network;
        :type divisionType: str
        :param customerGroup: Name of Customer Group, just to differenciate Customers,  max 80 Characters
        :type customerGroup: str
        :param idRef: ID n Reference System, max 40 Characters
        :type idRef: str
        :return: returns the TK of the newly inserted Customer, otherwise '-1'.
        :rtype: str
        :description: This is a wrapper method for AddNewCustomer() from toolkit; Watch out for errors for more information.
        """
        Tk, error = self.toolkit.AddNewCustomer(x, y, z, symbolFactor, fkHouse, consumption, counterId, 
                                             customerId, dimension, divisionType, customerGroup, idRef)
        if Tk == "-1":
            print("Error : " + error)
        return Tk
    
    def AddNewValveOnPipe(self, tkPipe: str, iSymbolType, position: np.float32, name: str, description: str,
             isPostureStatic, fkSWVT: str, openClose: bool, idRef: str):
        """
        Insert a new Net Valve of Pipe. If the Pipe does'nt lie on the main Container, nothing shall be done.

        :param tkPipe: The tk (key) of the Pipe 
        :type tkPipe: str
        :param iSymbolType: Symbol Type:
        Possible values are: 
         1 = Gate Valve
         2 = Flap Valve
         3 = Plug Valve
        :type iSymbolType: Interfaces.NetValveTypes
        :param position: Position on Pipe: Possible Values are: 
          0 = at the Beginning of the Pipe (by Node Ki)
         -1 = at the End of the Pipe (by Node Kk)
         -2 = at the Middle of the Pipe
          or every Value in the interval [0, L] where L is the technical Length of the Pipe. 
        :type position: np.float32
        :param name: A Name for the Valve, max 40 Characters
        :type name: str
        :param description: Description of the Valve, max 254 Characters 
        :type description: str
        :param isPostureStatic: Option if the Posture is statically open/closed or time depemdant. 
         Enter NetValvePostures.STATIC_OPEN_CLOSE if Posture is always open / closed
         otherwise enter NetValvePostures.TIME_DEP_TABLE if the Posture depends on a Setpoint Table (SWVT)
        :type isPostureStatic: Interfaces.NetValvePostures
        :param fkSWVT: the pk (key) of the SetPoint Table, in Case the Parameter 'isPostureStatic' is entered as NetValvePostures.TIME_DEP_TABLE
        :type fkSWVT: str
        :param openClose: Only usable in Case the Parameter 'isPostureStatic' is entered as NetValvePostures.STATIC_OPEN_CLOSE. So entering
         in that case 'True', resp. 'False' assumes the Valve is always open resp. closed.
        :type openClose: bool
        :param idRef: Reference ID, max 40 Characters 
        :type idRef: str
        :return: returns the TK of the newly inserted Valve, otherwise '-1'.
        :rtype: str
        :description: This is a wrapper method for AddNewValveOnPipe() from toolkit; Watch out for errors for more information.
        """
        Tk, error = self.toolkit.AddNewValveOnPipe(tkPipe, iSymbolType, position, name, description, isPostureStatic, fkSWVT, openClose, idRef)
        if Tk == "-1":
            print("Error : " + error)
        return Tk
        
        
    def AddNewHydrant(self, x: np.float64, y: np.float64, z: np.float64, iType, symbolFactor: np.float64, fkNode: str, L: np.float32, dn: np.float32, roughness: np.float32,
            ph_min: np.float32, ph_soll: np.float32, qm_soll, activity,
            idRef: str, name: str, description: str):
        """
        Method for inserting a new Customer within the main Container of the Model

        :param x: The X-Coordinate of the Hydrant
        :type x: np.float64
        :param y: The Y-Coordinate of the Hydrant
        :type y: np.float64
        :param z: The Z-Coordinate of the Hydrant
        :type z: np.float32
        :param iType: Type of Hydrant. Possible Value are:
           1 = Subsurface
          11 = Surface
        :type iType: Interfaces.Hydrant_Type
        :param symbolFactor: The Symbol Factor
        :type symbolFactor: np.float64
        :param fkNode: The tk (key) of a Node within the main Comntainer if the Hydrant is attached to a Node
        :type fkNode: str
        :param L: Length of the Connection Pipe
        :type L: np.float32
        :param dn: Nominal Diameter of the Hydrant in [mm]
        :type dn: np.float32
        :param roughness: Roughness coefficient (k-value) Connecting pipe
        :type roughness: np.float32
        :param ph_min: Minimum pressure at the tapping point
        :type ph_min: np.float32
        :param ph_soll: Set pressure at the binding point
        :type ph_soll: np.float32
        :param qm_soll: Target extraction quantity
        :type qm_soll: Interfaces.Hydrant_QM_SOLL
        :param activity: Activity status (0=inactive | 1=calculated in the extinguishing water plugin | 2=calculated)
        :type activity: Interfaces.Hydrant_Activity
        :param idRef: Reference ID
        :type idRef: str
        :param name: Name of the Hydrant, max 40 Characters
        :type name: str
        :param description: Description, max 254 Characters
        :type description: str
        :return: returns the TK of the newly inserted Hydrant, otherwise '-1'.
        :rtype: str
        :description: This is a wrapper method for AddNewHydrant() from toolkit; Watch out for errors for more information.
        """
        Tk, error = self.toolkit.AddNewHydrant(x, y, z, iType, symbolFactor, fkNode, L, dn, roughness, ph_min, ph_soll, qm_soll, activity, idRef, name, description)
        if Tk == "-1":
            print("Error : " + error)
        return Tk
        

# End of file




    
    
